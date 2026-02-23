<<<<<<< HEAD
import datetime
import logging
import time

import click
from sqlalchemy.exc import SQLAlchemyError

import app
from configs import dify_config
from enums.cloud_plan import CloudPlan
from extensions.ext_database import db
from extensions.ext_redis import redis_client
from models.model import (
    App,
    Message,
    MessageAgentThought,
    MessageAnnotation,
    MessageChain,
    MessageFeedback,
    MessageFile,
)
from models.web import SavedMessage
from services.feature_service import FeatureService

logger = logging.getLogger(__name__)


@app.celery.task(queue="dataset")
def clean_messages():
    click.echo(click.style("Start clean messages.", fg="green"))
    start_at = time.perf_counter()
    plan_sandbox_clean_message_day = datetime.datetime.now() - datetime.timedelta(
        days=dify_config.PLAN_SANDBOX_CLEAN_MESSAGE_DAY_SETTING
    )
    while True:
        try:
            # Main query with join and filter
            messages = (
                db.session.query(Message)
                .where(Message.created_at < plan_sandbox_clean_message_day)
                .order_by(Message.created_at.desc())
                .limit(100)
                .all()
            )

        except SQLAlchemyError:
            raise
        if not messages:
            break
        for message in messages:
            app = db.session.query(App).filter_by(id=message.app_id).first()
            if not app:
                logger.warning(
                    "Expected App record to exist, but none was found, app_id=%s, message_id=%s",
                    message.app_id,
                    message.id,
                )
                continue
            features_cache_key = f"features:{app.tenant_id}"
            plan_cache = redis_client.get(features_cache_key)
            if plan_cache is None:
                features = FeatureService.get_features(app.tenant_id)
                redis_client.setex(features_cache_key, 600, features.billing.subscription.plan)
                plan = features.billing.subscription.plan
            else:
                plan = plan_cache.decode()
            if plan == CloudPlan.SANDBOX:
                # clean related message
                db.session.query(MessageFeedback).where(MessageFeedback.message_id == message.id).delete(
                    synchronize_session=False
                )
                db.session.query(MessageAnnotation).where(MessageAnnotation.message_id == message.id).delete(
                    synchronize_session=False
                )
                db.session.query(MessageChain).where(MessageChain.message_id == message.id).delete(
                    synchronize_session=False
                )
                db.session.query(MessageAgentThought).where(MessageAgentThought.message_id == message.id).delete(
                    synchronize_session=False
                )
                db.session.query(MessageFile).where(MessageFile.message_id == message.id).delete(
                    synchronize_session=False
                )
                db.session.query(SavedMessage).where(SavedMessage.message_id == message.id).delete(
                    synchronize_session=False
                )
                db.session.query(Message).where(Message.id == message.id).delete()
                db.session.commit()
    end_at = time.perf_counter()
    click.echo(click.style(f"Cleaned messages from db success latency: {end_at - start_at}", fg="green"))
=======
import logging
import time

import click
from redis.exceptions import LockError

import app
from configs import dify_config
from extensions.ext_redis import redis_client
from services.retention.conversation.messages_clean_policy import create_message_clean_policy
from services.retention.conversation.messages_clean_service import MessagesCleanService

logger = logging.getLogger(__name__)


@app.celery.task(queue="retention")
def clean_messages():
    """
    Clean expired messages based on clean policy.

    This task uses MessagesCleanService to efficiently clean messages in batches.
    The behavior depends on BILLING_ENABLED configuration:
    - BILLING_ENABLED=True: only delete messages from sandbox tenants (with whitelist/grace period)
    - BILLING_ENABLED=False: delete all messages within the time range
    """
    click.echo(click.style("clean_messages: start clean messages.", fg="green"))
    start_at = time.perf_counter()

    try:
        # Create policy based on billing configuration
        policy = create_message_clean_policy(
            graceful_period_days=dify_config.SANDBOX_EXPIRED_RECORDS_CLEAN_GRACEFUL_PERIOD,
        )

        # Create and run the cleanup service
        # lock the task to avoid concurrent execution in case of the future data volume growth
        with redis_client.lock(
            "retention:clean_messages", timeout=dify_config.SANDBOX_EXPIRED_RECORDS_CLEAN_TASK_LOCK_TTL, blocking=False
        ):
            service = MessagesCleanService.from_days(
                policy=policy,
                days=dify_config.SANDBOX_EXPIRED_RECORDS_RETENTION_DAYS,
                batch_size=dify_config.SANDBOX_EXPIRED_RECORDS_CLEAN_BATCH_SIZE,
            )
            stats = service.run()

        end_at = time.perf_counter()
        click.echo(
            click.style(
                f"clean_messages: completed successfully\n"
                f"  - Latency: {end_at - start_at:.2f}s\n"
                f"  - Batches processed: {stats['batches']}\n"
                f"  - Total messages scanned: {stats['total_messages']}\n"
                f"  - Messages filtered: {stats['filtered_messages']}\n"
                f"  - Messages deleted: {stats['total_deleted']}",
                fg="green",
            )
        )
    except LockError:
        end_at = time.perf_counter()
        logger.exception("clean_messages: acquire task lock failed, skip current execution")
        click.echo(
            click.style(
                f"clean_messages: skipped (lock already held) - latency: {end_at - start_at:.2f}s",
                fg="yellow",
            )
        )
        raise
    except Exception as e:
        end_at = time.perf_counter()
        logger.exception("clean_messages failed")
        click.echo(
            click.style(
                f"clean_messages: failed after {end_at - start_at:.2f}s - {str(e)}",
                fg="red",
            )
        )
        raise
>>>>>>> upstream/main
