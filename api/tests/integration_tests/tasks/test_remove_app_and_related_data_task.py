<<<<<<< HEAD
import uuid
from unittest.mock import patch

import pytest
from sqlalchemy import delete

from core.variables.segments import StringSegment
from extensions.ext_database import db
from models import Tenant
from models.enums import CreatorUserRole
from models.model import App, UploadFile
from models.workflow import WorkflowDraftVariable, WorkflowDraftVariableFile
from tasks.remove_app_and_related_data_task import _delete_draft_variables, delete_draft_variables_batch


@pytest.fixture
def app_and_tenant(flask_req_ctx):
    tenant_id = uuid.uuid4()
    tenant = Tenant(
        id=tenant_id,
        name="test_tenant",
    )
    db.session.add(tenant)

    app = App(
        tenant_id=tenant_id,  # Now tenant.id will have a value
        name=f"Test App for tenant {tenant.id}",
        mode="workflow",
        enable_site=True,
        enable_api=True,
    )
    db.session.add(app)
    db.session.flush()
    yield (tenant, app)

    # Cleanup with proper error handling
    db.session.delete(app)
    db.session.delete(tenant)


class TestDeleteDraftVariablesIntegration:
    @pytest.fixture
    def setup_test_data(self, app_and_tenant):
        """Create test data with apps and draft variables."""
        tenant, app = app_and_tenant

        # Create a second app for testing
        app2 = App(
            tenant_id=tenant.id,
            name="Test App 2",
            mode="workflow",
            enable_site=True,
            enable_api=True,
        )
        db.session.add(app2)
        db.session.commit()

        # Create draft variables for both apps
        variables_app1 = []
        variables_app2 = []

        for i in range(5):
            var1 = WorkflowDraftVariable.new_node_variable(
                app_id=app.id,
                node_id=f"node_{i}",
                name=f"var_{i}",
                value=StringSegment(value="test_value"),
                node_execution_id=str(uuid.uuid4()),
            )
            db.session.add(var1)
            variables_app1.append(var1)

            var2 = WorkflowDraftVariable.new_node_variable(
                app_id=app2.id,
                node_id=f"node_{i}",
                name=f"var_{i}",
                value=StringSegment(value="test_value"),
                node_execution_id=str(uuid.uuid4()),
            )
            db.session.add(var2)
            variables_app2.append(var2)

        # Commit all the variables to the database
        db.session.commit()

        yield {
            "app1": app,
            "app2": app2,
            "tenant": tenant,
            "variables_app1": variables_app1,
            "variables_app2": variables_app2,
        }

        # Cleanup - refresh session and check if objects still exist
        db.session.rollback()  # Clear any pending changes

        # Clean up remaining variables
        cleanup_query = (
            delete(WorkflowDraftVariable)
            .where(
                WorkflowDraftVariable.app_id.in_([app.id, app2.id]),
            )
            .execution_options(synchronize_session=False)
        )
        db.session.execute(cleanup_query)

        # Clean up app2
        app2_obj = db.session.get(App, app2.id)
        if app2_obj:
            db.session.delete(app2_obj)

        db.session.commit()

    def test_delete_draft_variables_batch_removes_correct_variables(self, setup_test_data):
        """Test that batch deletion only removes variables for the specified app."""
        data = setup_test_data
        app1_id = data["app1"].id
        app2_id = data["app2"].id

        # Verify initial state
        app1_vars_before = db.session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
        app2_vars_before = db.session.query(WorkflowDraftVariable).filter_by(app_id=app2_id).count()
        assert app1_vars_before == 5
        assert app2_vars_before == 5

        # Delete app1 variables
        deleted_count = delete_draft_variables_batch(app1_id, batch_size=10)

        # Verify results
        assert deleted_count == 5

        app1_vars_after = db.session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
        app2_vars_after = db.session.query(WorkflowDraftVariable).filter_by(app_id=app2_id).count()

        assert app1_vars_after == 0  # All app1 variables deleted
        assert app2_vars_after == 5  # App2 variables unchanged

    def test_delete_draft_variables_batch_with_small_batch_size(self, setup_test_data):
        """Test batch deletion with small batch size processes all records."""
        data = setup_test_data
        app1_id = data["app1"].id

        # Use small batch size to force multiple batches
        deleted_count = delete_draft_variables_batch(app1_id, batch_size=2)

        assert deleted_count == 5

        # Verify all variables are deleted
        remaining_vars = db.session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
        assert remaining_vars == 0

    def test_delete_draft_variables_batch_nonexistent_app(self, setup_test_data):
        """Test that deleting variables for nonexistent app returns 0."""
        nonexistent_app_id = str(uuid.uuid4())  # Use a valid UUID format

        deleted_count = delete_draft_variables_batch(nonexistent_app_id, batch_size=100)

        assert deleted_count == 0

    def test_delete_draft_variables_wrapper_function(self, setup_test_data):
        """Test that _delete_draft_variables wrapper function works correctly."""
        data = setup_test_data
        app1_id = data["app1"].id

        # Verify initial state
        vars_before = db.session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
        assert vars_before == 5

        # Call wrapper function
        deleted_count = _delete_draft_variables(app1_id)

        # Verify results
        assert deleted_count == 5

        vars_after = db.session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
        assert vars_after == 0

    def test_batch_deletion_handles_large_dataset(self, app_and_tenant):
        """Test batch deletion with larger dataset to verify batching logic."""
        tenant, app = app_and_tenant

        # Create many draft variables
        variables = []
        for i in range(25):
            var = WorkflowDraftVariable.new_node_variable(
                app_id=app.id,
                node_id=f"node_{i}",
                name=f"var_{i}",
                value=StringSegment(value="test_value"),
                node_execution_id=str(uuid.uuid4()),
            )
            db.session.add(var)
            variables.append(var)
        variable_ids = [i.id for i in variables]

        # Commit the variables to the database
        db.session.commit()

        try:
            # Use small batch size to force multiple batches
            deleted_count = delete_draft_variables_batch(app.id, batch_size=8)

            assert deleted_count == 25

            # Verify all variables are deleted
            remaining_vars = db.session.query(WorkflowDraftVariable).filter_by(app_id=app.id).count()
            assert remaining_vars == 0

        finally:
            query = (
                delete(WorkflowDraftVariable)
                .where(
                    WorkflowDraftVariable.id.in_(variable_ids),
                )
                .execution_options(synchronize_session=False)
            )
            db.session.execute(query)


class TestDeleteDraftVariablesWithOffloadIntegration:
    """Integration tests for draft variable deletion with Offload data."""

    @pytest.fixture
    def setup_offload_test_data(self, app_and_tenant):
        """Create test data with draft variables that have associated Offload files."""
        tenant, app = app_and_tenant

        # Create UploadFile records
        from libs.datetime_utils import naive_utc_now

        upload_file1 = UploadFile(
            tenant_id=tenant.id,
            storage_type="local",
            key="test/file1.json",
            name="file1.json",
            size=1024,
            extension="json",
            mime_type="application/json",
            created_by_role=CreatorUserRole.ACCOUNT,
            created_by=str(uuid.uuid4()),
            created_at=naive_utc_now(),
            used=False,
        )
        upload_file2 = UploadFile(
            tenant_id=tenant.id,
            storage_type="local",
            key="test/file2.json",
            name="file2.json",
            size=2048,
            extension="json",
            mime_type="application/json",
            created_by_role=CreatorUserRole.ACCOUNT,
            created_by=str(uuid.uuid4()),
            created_at=naive_utc_now(),
            used=False,
        )
        db.session.add(upload_file1)
        db.session.add(upload_file2)
        db.session.flush()

        # Create WorkflowDraftVariableFile records
        from core.variables.types import SegmentType

        var_file1 = WorkflowDraftVariableFile(
            tenant_id=tenant.id,
            app_id=app.id,
            user_id=str(uuid.uuid4()),
            upload_file_id=upload_file1.id,
            size=1024,
            length=10,
            value_type=SegmentType.STRING,
        )
        var_file2 = WorkflowDraftVariableFile(
            tenant_id=tenant.id,
            app_id=app.id,
            user_id=str(uuid.uuid4()),
            upload_file_id=upload_file2.id,
            size=2048,
            length=20,
            value_type=SegmentType.OBJECT,
        )
        db.session.add(var_file1)
        db.session.add(var_file2)
        db.session.flush()

        # Create WorkflowDraftVariable records with file associations
        draft_var1 = WorkflowDraftVariable.new_node_variable(
            app_id=app.id,
            node_id="node_1",
            name="large_var_1",
            value=StringSegment(value="truncated..."),
            node_execution_id=str(uuid.uuid4()),
            file_id=var_file1.id,
        )
        draft_var2 = WorkflowDraftVariable.new_node_variable(
            app_id=app.id,
            node_id="node_2",
            name="large_var_2",
            value=StringSegment(value="truncated..."),
            node_execution_id=str(uuid.uuid4()),
            file_id=var_file2.id,
        )
        # Create a regular variable without Offload data
        draft_var3 = WorkflowDraftVariable.new_node_variable(
            app_id=app.id,
            node_id="node_3",
            name="regular_var",
            value=StringSegment(value="regular_value"),
            node_execution_id=str(uuid.uuid4()),
        )

        db.session.add(draft_var1)
        db.session.add(draft_var2)
        db.session.add(draft_var3)
        db.session.commit()

        yield {
            "app": app,
            "tenant": tenant,
            "upload_files": [upload_file1, upload_file2],
            "variable_files": [var_file1, var_file2],
            "draft_variables": [draft_var1, draft_var2, draft_var3],
        }

        # Cleanup
        db.session.rollback()

        # Clean up any remaining records
        for table, ids in [
            (WorkflowDraftVariable, [v.id for v in [draft_var1, draft_var2, draft_var3]]),
            (WorkflowDraftVariableFile, [vf.id for vf in [var_file1, var_file2]]),
            (UploadFile, [uf.id for uf in [upload_file1, upload_file2]]),
        ]:
            cleanup_query = delete(table).where(table.id.in_(ids)).execution_options(synchronize_session=False)
            db.session.execute(cleanup_query)

        db.session.commit()

    @patch("extensions.ext_storage.storage")
    def test_delete_draft_variables_with_offload_data(self, mock_storage, setup_offload_test_data):
        """Test that deleting draft variables also cleans up associated Offload data."""
        data = setup_offload_test_data
        app_id = data["app"].id

        # Mock storage deletion to succeed
        mock_storage.delete.return_value = None

        # Verify initial state
        draft_vars_before = db.session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
        var_files_before = db.session.query(WorkflowDraftVariableFile).count()
        upload_files_before = db.session.query(UploadFile).count()

        assert draft_vars_before == 3  # 2 with files + 1 regular
        assert var_files_before == 2
        assert upload_files_before == 2

        # Delete draft variables
        deleted_count = delete_draft_variables_batch(app_id, batch_size=10)

        # Verify results
        assert deleted_count == 3

        # Check that all draft variables are deleted
        draft_vars_after = db.session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
        assert draft_vars_after == 0

        # Check that associated Offload data is cleaned up
        var_files_after = db.session.query(WorkflowDraftVariableFile).count()
        upload_files_after = db.session.query(UploadFile).count()

        assert var_files_after == 0  # All variable files should be deleted
        assert upload_files_after == 0  # All upload files should be deleted

        # Verify storage deletion was called for both files
        assert mock_storage.delete.call_count == 2
        storage_keys_deleted = [call.args[0] for call in mock_storage.delete.call_args_list]
        assert "test/file1.json" in storage_keys_deleted
        assert "test/file2.json" in storage_keys_deleted

    @patch("extensions.ext_storage.storage")
    def test_delete_draft_variables_storage_failure_continues_cleanup(self, mock_storage, setup_offload_test_data):
        """Test that database cleanup continues even when storage deletion fails."""
        data = setup_offload_test_data
        app_id = data["app"].id

        # Mock storage deletion to fail for first file, succeed for second
        mock_storage.delete.side_effect = [Exception("Storage error"), None]

        # Delete draft variables
        deleted_count = delete_draft_variables_batch(app_id, batch_size=10)

        # Verify that all draft variables are still deleted
        assert deleted_count == 3

        draft_vars_after = db.session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
        assert draft_vars_after == 0

        # Database cleanup should still succeed even with storage errors
        var_files_after = db.session.query(WorkflowDraftVariableFile).count()
        upload_files_after = db.session.query(UploadFile).count()

        assert var_files_after == 0
        assert upload_files_after == 0

        # Verify storage deletion was attempted for both files
        assert mock_storage.delete.call_count == 2

    @patch("extensions.ext_storage.storage")
    def test_delete_draft_variables_partial_offload_data(self, mock_storage, setup_offload_test_data):
        """Test deletion with mix of variables with and without Offload data."""
        data = setup_offload_test_data
        app_id = data["app"].id

        # Create additional app with only regular variables (no offload data)
        tenant = data["tenant"]
        app2 = App(
            tenant_id=tenant.id,
            name="Test App 2",
            mode="workflow",
            enable_site=True,
            enable_api=True,
        )
        db.session.add(app2)
        db.session.flush()

        # Add regular variables to app2
        regular_vars = []
        for i in range(3):
            var = WorkflowDraftVariable.new_node_variable(
                app_id=app2.id,
                node_id=f"node_{i}",
                name=f"var_{i}",
                value=StringSegment(value="regular_value"),
                node_execution_id=str(uuid.uuid4()),
            )
            db.session.add(var)
            regular_vars.append(var)
        db.session.commit()

        try:
            # Mock storage deletion
            mock_storage.delete.return_value = None

            # Delete variables for app2 (no offload data)
            deleted_count_app2 = delete_draft_variables_batch(app2.id, batch_size=10)
            assert deleted_count_app2 == 3

            # Verify storage wasn't called for app2 (no offload files)
            mock_storage.delete.assert_not_called()

            # Delete variables for original app (with offload data)
            deleted_count_app1 = delete_draft_variables_batch(app_id, batch_size=10)
            assert deleted_count_app1 == 3

            # Now storage should be called for the offload files
            assert mock_storage.delete.call_count == 2

        finally:
            # Cleanup app2 and its variables
            cleanup_vars_query = (
                delete(WorkflowDraftVariable)
                .where(WorkflowDraftVariable.app_id == app2.id)
                .execution_options(synchronize_session=False)
            )
            db.session.execute(cleanup_vars_query)

            app2_obj = db.session.get(App, app2.id)
            if app2_obj:
                db.session.delete(app2_obj)
            db.session.commit()
=======
import uuid
from unittest.mock import patch

import pytest
from sqlalchemy import delete

from core.db.session_factory import session_factory
from core.variables.segments import StringSegment
from models import Tenant
from models.enums import CreatorUserRole
from models.model import App, UploadFile
from models.workflow import WorkflowDraftVariable, WorkflowDraftVariableFile
from tasks.remove_app_and_related_data_task import (
    _delete_draft_variables,
    delete_draft_variables_batch,
)


@pytest.fixture
def app_and_tenant(flask_req_ctx):
    tenant_id = uuid.uuid4()
    with session_factory.create_session() as session:
        tenant = Tenant(name="test_tenant")
        session.add(tenant)
        session.flush()

        app = App(
            tenant_id=tenant.id,
            name=f"Test App for tenant {tenant.id}",
            mode="workflow",
            enable_site=True,
            enable_api=True,
        )
        session.add(app)
        session.flush()

    # return detached objects (ids will be used by tests)
    return (tenant, app)


class TestDeleteDraftVariablesIntegration:
    @pytest.fixture
    def setup_test_data(self, app_and_tenant):
        """Create test data with apps and draft variables."""
        tenant, app = app_and_tenant

        with session_factory.create_session() as session:
            app2 = App(
                tenant_id=tenant.id,
                name="Test App 2",
                mode="workflow",
                enable_site=True,
                enable_api=True,
            )
            session.add(app2)
            session.flush()

            variables_app1 = []
            variables_app2 = []
            for i in range(5):
                var1 = WorkflowDraftVariable.new_node_variable(
                    app_id=app.id,
                    node_id=f"node_{i}",
                    name=f"var_{i}",
                    value=StringSegment(value="test_value"),
                    node_execution_id=str(uuid.uuid4()),
                )
                session.add(var1)
                variables_app1.append(var1)

                var2 = WorkflowDraftVariable.new_node_variable(
                    app_id=app2.id,
                    node_id=f"node_{i}",
                    name=f"var_{i}",
                    value=StringSegment(value="test_value"),
                    node_execution_id=str(uuid.uuid4()),
                )
                session.add(var2)
                variables_app2.append(var2)
            session.commit()

            app2_id = app2.id

        yield {
            "app1": app,
            "app2": App(id=app2_id),  # dummy with id to avoid open session
            "tenant": tenant,
            "variables_app1": variables_app1,
            "variables_app2": variables_app2,
        }

        with session_factory.create_session() as session:
            cleanup_query = (
                delete(WorkflowDraftVariable)
                .where(WorkflowDraftVariable.app_id.in_([app.id, app2_id]))
                .execution_options(synchronize_session=False)
            )
            session.execute(cleanup_query)
            app2_obj = session.get(App, app2_id)
            if app2_obj:
                session.delete(app2_obj)
            session.commit()

    def test_delete_draft_variables_batch_removes_correct_variables(self, setup_test_data):
        data = setup_test_data
        app1_id = data["app1"].id
        app2_id = data["app2"].id

        with session_factory.create_session() as session:
            app1_vars_before = session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
            app2_vars_before = session.query(WorkflowDraftVariable).filter_by(app_id=app2_id).count()
        assert app1_vars_before == 5
        assert app2_vars_before == 5

        deleted_count = delete_draft_variables_batch(app1_id, batch_size=10)
        assert deleted_count == 5

        with session_factory.create_session() as session:
            app1_vars_after = session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
            app2_vars_after = session.query(WorkflowDraftVariable).filter_by(app_id=app2_id).count()
        assert app1_vars_after == 0
        assert app2_vars_after == 5

    def test_delete_draft_variables_batch_with_small_batch_size(self, setup_test_data):
        data = setup_test_data
        app1_id = data["app1"].id

        deleted_count = delete_draft_variables_batch(app1_id, batch_size=2)
        assert deleted_count == 5

        with session_factory.create_session() as session:
            remaining_vars = session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
        assert remaining_vars == 0

    def test_delete_draft_variables_batch_nonexistent_app(self, setup_test_data):
        nonexistent_app_id = str(uuid.uuid4())
        deleted_count = delete_draft_variables_batch(nonexistent_app_id, batch_size=100)
        assert deleted_count == 0

    def test_delete_draft_variables_wrapper_function(self, setup_test_data):
        data = setup_test_data
        app1_id = data["app1"].id

        with session_factory.create_session() as session:
            vars_before = session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
        assert vars_before == 5

        deleted_count = _delete_draft_variables(app1_id)
        assert deleted_count == 5

        with session_factory.create_session() as session:
            vars_after = session.query(WorkflowDraftVariable).filter_by(app_id=app1_id).count()
        assert vars_after == 0

    def test_batch_deletion_handles_large_dataset(self, app_and_tenant):
        tenant, app = app_and_tenant
        variable_ids: list[str] = []
        with session_factory.create_session() as session:
            variables = []
            for i in range(25):
                var = WorkflowDraftVariable.new_node_variable(
                    app_id=app.id,
                    node_id=f"node_{i}",
                    name=f"var_{i}",
                    value=StringSegment(value="test_value"),
                    node_execution_id=str(uuid.uuid4()),
                )
                session.add(var)
                variables.append(var)
            session.commit()
            variable_ids = [v.id for v in variables]

        try:
            deleted_count = delete_draft_variables_batch(app.id, batch_size=8)
            assert deleted_count == 25
            with session_factory.create_session() as session:
                remaining = session.query(WorkflowDraftVariable).filter_by(app_id=app.id).count()
            assert remaining == 0
        finally:
            with session_factory.create_session() as session:
                query = (
                    delete(WorkflowDraftVariable)
                    .where(WorkflowDraftVariable.id.in_(variable_ids))
                    .execution_options(synchronize_session=False)
                )
                session.execute(query)
                session.commit()


class TestDeleteDraftVariablesWithOffloadIntegration:
    @pytest.fixture
    def setup_offload_test_data(self, app_and_tenant):
        tenant, app = app_and_tenant
        from core.variables.types import SegmentType
        from libs.datetime_utils import naive_utc_now

        with session_factory.create_session() as session:
            upload_file1 = UploadFile(
                tenant_id=tenant.id,
                storage_type="local",
                key="test/file1.json",
                name="file1.json",
                size=1024,
                extension="json",
                mime_type="application/json",
                created_by_role=CreatorUserRole.ACCOUNT,
                created_by=str(uuid.uuid4()),
                created_at=naive_utc_now(),
                used=False,
            )
            upload_file2 = UploadFile(
                tenant_id=tenant.id,
                storage_type="local",
                key="test/file2.json",
                name="file2.json",
                size=2048,
                extension="json",
                mime_type="application/json",
                created_by_role=CreatorUserRole.ACCOUNT,
                created_by=str(uuid.uuid4()),
                created_at=naive_utc_now(),
                used=False,
            )
            session.add(upload_file1)
            session.add(upload_file2)
            session.flush()

            var_file1 = WorkflowDraftVariableFile(
                tenant_id=tenant.id,
                app_id=app.id,
                user_id=str(uuid.uuid4()),
                upload_file_id=upload_file1.id,
                size=1024,
                length=10,
                value_type=SegmentType.STRING,
            )
            var_file2 = WorkflowDraftVariableFile(
                tenant_id=tenant.id,
                app_id=app.id,
                user_id=str(uuid.uuid4()),
                upload_file_id=upload_file2.id,
                size=2048,
                length=20,
                value_type=SegmentType.OBJECT,
            )
            session.add(var_file1)
            session.add(var_file2)
            session.flush()

            draft_var1 = WorkflowDraftVariable.new_node_variable(
                app_id=app.id,
                node_id="node_1",
                name="large_var_1",
                value=StringSegment(value="truncated..."),
                node_execution_id=str(uuid.uuid4()),
                file_id=var_file1.id,
            )
            draft_var2 = WorkflowDraftVariable.new_node_variable(
                app_id=app.id,
                node_id="node_2",
                name="large_var_2",
                value=StringSegment(value="truncated..."),
                node_execution_id=str(uuid.uuid4()),
                file_id=var_file2.id,
            )
            draft_var3 = WorkflowDraftVariable.new_node_variable(
                app_id=app.id,
                node_id="node_3",
                name="regular_var",
                value=StringSegment(value="regular_value"),
                node_execution_id=str(uuid.uuid4()),
            )
            session.add(draft_var1)
            session.add(draft_var2)
            session.add(draft_var3)
            session.commit()

            data = {
                "app": app,
                "tenant": tenant,
                "upload_files": [upload_file1, upload_file2],
                "variable_files": [var_file1, var_file2],
                "draft_variables": [draft_var1, draft_var2, draft_var3],
            }

        yield data

        with session_factory.create_session() as session:
            session.rollback()
            for table, ids in [
                (WorkflowDraftVariable, [v.id for v in data["draft_variables"]]),
                (WorkflowDraftVariableFile, [vf.id for vf in data["variable_files"]]),
                (UploadFile, [uf.id for uf in data["upload_files"]]),
            ]:
                cleanup_query = delete(table).where(table.id.in_(ids)).execution_options(synchronize_session=False)
                session.execute(cleanup_query)
            session.commit()

    @patch("extensions.ext_storage.storage")
    def test_delete_draft_variables_with_offload_data(self, mock_storage, setup_offload_test_data):
        data = setup_offload_test_data
        app_id = data["app"].id
        upload_file_ids = [uf.id for uf in data["upload_files"]]
        variable_file_ids = [vf.id for vf in data["variable_files"]]
        mock_storage.delete.return_value = None

        with session_factory.create_session() as session:
            draft_vars_before = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
            var_files_before = (
                session.query(WorkflowDraftVariableFile)
                .where(WorkflowDraftVariableFile.id.in_(variable_file_ids))
                .count()
            )
            upload_files_before = session.query(UploadFile).where(UploadFile.id.in_(upload_file_ids)).count()
        assert draft_vars_before == 3
        assert var_files_before == 2
        assert upload_files_before == 2

        deleted_count = delete_draft_variables_batch(app_id, batch_size=10)
        assert deleted_count == 3

        with session_factory.create_session() as session:
            draft_vars_after = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
        assert draft_vars_after == 0

        with session_factory.create_session() as session:
            var_files_after = (
                session.query(WorkflowDraftVariableFile)
                .where(WorkflowDraftVariableFile.id.in_(variable_file_ids))
                .count()
            )
            upload_files_after = session.query(UploadFile).where(UploadFile.id.in_(upload_file_ids)).count()
        assert var_files_after == 0
        assert upload_files_after == 0

        assert mock_storage.delete.call_count == 2
        storage_keys_deleted = [call.args[0] for call in mock_storage.delete.call_args_list]
        assert "test/file1.json" in storage_keys_deleted
        assert "test/file2.json" in storage_keys_deleted

    @patch("extensions.ext_storage.storage")
    def test_delete_draft_variables_storage_failure_continues_cleanup(self, mock_storage, setup_offload_test_data):
        data = setup_offload_test_data
        app_id = data["app"].id
        upload_file_ids = [uf.id for uf in data["upload_files"]]
        variable_file_ids = [vf.id for vf in data["variable_files"]]
        mock_storage.delete.side_effect = [Exception("Storage error"), None]

        deleted_count = delete_draft_variables_batch(app_id, batch_size=10)
        assert deleted_count == 3

        with session_factory.create_session() as session:
            draft_vars_after = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
        assert draft_vars_after == 0

        with session_factory.create_session() as session:
            var_files_after = (
                session.query(WorkflowDraftVariableFile)
                .where(WorkflowDraftVariableFile.id.in_(variable_file_ids))
                .count()
            )
            upload_files_after = session.query(UploadFile).where(UploadFile.id.in_(upload_file_ids)).count()
        assert var_files_after == 0
        assert upload_files_after == 0

        assert mock_storage.delete.call_count == 2

    @patch("extensions.ext_storage.storage")
    def test_delete_draft_variables_partial_offload_data(self, mock_storage, setup_offload_test_data):
        data = setup_offload_test_data
        app_id = data["app"].id
        tenant = data["tenant"]

        with session_factory.create_session() as session:
            app2 = App(
                tenant_id=tenant.id,
                name="Test App 2",
                mode="workflow",
                enable_site=True,
                enable_api=True,
            )
            session.add(app2)
            session.flush()

            for i in range(3):
                var = WorkflowDraftVariable.new_node_variable(
                    app_id=app2.id,
                    node_id=f"node_{i}",
                    name=f"var_{i}",
                    value=StringSegment(value="regular_value"),
                    node_execution_id=str(uuid.uuid4()),
                )
                session.add(var)
            session.commit()

        try:
            mock_storage.delete.return_value = None
            deleted_count_app2 = delete_draft_variables_batch(app2.id, batch_size=10)
            assert deleted_count_app2 == 3
            mock_storage.delete.assert_not_called()

            deleted_count_app1 = delete_draft_variables_batch(app_id, batch_size=10)
            assert deleted_count_app1 == 3
            assert mock_storage.delete.call_count == 2
        finally:
            with session_factory.create_session() as session:
                cleanup_vars_query = (
                    delete(WorkflowDraftVariable)
                    .where(WorkflowDraftVariable.app_id == app2.id)
                    .execution_options(synchronize_session=False)
                )
                session.execute(cleanup_vars_query)
                app2_obj = session.get(App, app2.id)
                if app2_obj:
                    session.delete(app2_obj)
                session.commit()


class TestDeleteDraftVariablesSessionCommit:
    """Test suite to verify session commit behavior in delete_draft_variables_batch."""

    @pytest.fixture
    def setup_offload_test_data(self, app_and_tenant):
        """Create test data with offload files for session commit tests."""
        from core.variables.types import SegmentType
        from libs.datetime_utils import naive_utc_now

        tenant, app = app_and_tenant

        with session_factory.create_session() as session:
            upload_file1 = UploadFile(
                tenant_id=tenant.id,
                storage_type="local",
                key="test/file1.json",
                name="file1.json",
                size=1024,
                extension="json",
                mime_type="application/json",
                created_by_role=CreatorUserRole.ACCOUNT,
                created_by=str(uuid.uuid4()),
                created_at=naive_utc_now(),
                used=False,
            )
            upload_file2 = UploadFile(
                tenant_id=tenant.id,
                storage_type="local",
                key="test/file2.json",
                name="file2.json",
                size=2048,
                extension="json",
                mime_type="application/json",
                created_by_role=CreatorUserRole.ACCOUNT,
                created_by=str(uuid.uuid4()),
                created_at=naive_utc_now(),
                used=False,
            )
            session.add(upload_file1)
            session.add(upload_file2)
            session.flush()

            var_file1 = WorkflowDraftVariableFile(
                tenant_id=tenant.id,
                app_id=app.id,
                user_id=str(uuid.uuid4()),
                upload_file_id=upload_file1.id,
                size=1024,
                length=10,
                value_type=SegmentType.STRING,
            )
            var_file2 = WorkflowDraftVariableFile(
                tenant_id=tenant.id,
                app_id=app.id,
                user_id=str(uuid.uuid4()),
                upload_file_id=upload_file2.id,
                size=2048,
                length=20,
                value_type=SegmentType.OBJECT,
            )
            session.add(var_file1)
            session.add(var_file2)
            session.flush()

            draft_var1 = WorkflowDraftVariable.new_node_variable(
                app_id=app.id,
                node_id="node_1",
                name="large_var_1",
                value=StringSegment(value="truncated..."),
                node_execution_id=str(uuid.uuid4()),
                file_id=var_file1.id,
            )
            draft_var2 = WorkflowDraftVariable.new_node_variable(
                app_id=app.id,
                node_id="node_2",
                name="large_var_2",
                value=StringSegment(value="truncated..."),
                node_execution_id=str(uuid.uuid4()),
                file_id=var_file2.id,
            )
            draft_var3 = WorkflowDraftVariable.new_node_variable(
                app_id=app.id,
                node_id="node_3",
                name="regular_var",
                value=StringSegment(value="regular_value"),
                node_execution_id=str(uuid.uuid4()),
            )
            session.add(draft_var1)
            session.add(draft_var2)
            session.add(draft_var3)
            session.commit()

            data = {
                "app": app,
                "tenant": tenant,
                "upload_files": [upload_file1, upload_file2],
                "variable_files": [var_file1, var_file2],
                "draft_variables": [draft_var1, draft_var2, draft_var3],
            }

        yield data

        with session_factory.create_session() as session:
            for table, ids in [
                (WorkflowDraftVariable, [v.id for v in data["draft_variables"]]),
                (WorkflowDraftVariableFile, [vf.id for vf in data["variable_files"]]),
                (UploadFile, [uf.id for uf in data["upload_files"]]),
            ]:
                cleanup_query = delete(table).where(table.id.in_(ids)).execution_options(synchronize_session=False)
                session.execute(cleanup_query)
            session.commit()

    @pytest.fixture
    def setup_commit_test_data(self, app_and_tenant):
        """Create test data for session commit tests."""
        tenant, app = app_and_tenant
        variable_ids: list[str] = []

        with session_factory.create_session() as session:
            variables = []
            for i in range(10):
                var = WorkflowDraftVariable.new_node_variable(
                    app_id=app.id,
                    node_id=f"node_{i}",
                    name=f"var_{i}",
                    value=StringSegment(value="test_value"),
                    node_execution_id=str(uuid.uuid4()),
                )
                session.add(var)
                variables.append(var)
            session.commit()
            variable_ids = [v.id for v in variables]

        yield {
            "app": app,
            "tenant": tenant,
            "variable_ids": variable_ids,
        }

        with session_factory.create_session() as session:
            cleanup_query = (
                delete(WorkflowDraftVariable)
                .where(WorkflowDraftVariable.id.in_(variable_ids))
                .execution_options(synchronize_session=False)
            )
            session.execute(cleanup_query)
            session.commit()

    def test_session_commit_is_called_after_each_batch(self, setup_commit_test_data):
        """Test that session.begin() is used for automatic transaction management."""
        data = setup_commit_test_data
        app_id = data["app"].id

        # Since session.begin() is used, the transaction is automatically committed
        # when the with block exits successfully. We verify this by checking that
        # data is actually persisted.
        deleted_count = delete_draft_variables_batch(app_id, batch_size=3)

        # Verify all data was deleted (proves transaction was committed)
        with session_factory.create_session() as session:
            remaining_count = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()

        assert deleted_count == 10
        assert remaining_count == 0

    def test_data_persisted_after_batch_deletion(self, setup_commit_test_data):
        """Test that data is actually persisted to database after batch deletion with commits."""
        data = setup_commit_test_data
        app_id = data["app"].id
        variable_ids = data["variable_ids"]

        # Verify initial state
        with session_factory.create_session() as session:
            initial_count = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
        assert initial_count == 10

        # Perform deletion with small batch size to force multiple commits
        deleted_count = delete_draft_variables_batch(app_id, batch_size=3)

        assert deleted_count == 10

        # Verify all data is deleted in a new session (proves commits worked)
        with session_factory.create_session() as session:
            final_count = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
        assert final_count == 0

        # Verify specific IDs are deleted
        with session_factory.create_session() as session:
            remaining_vars = (
                session.query(WorkflowDraftVariable).where(WorkflowDraftVariable.id.in_(variable_ids)).count()
            )
        assert remaining_vars == 0

    def test_session_commit_with_empty_dataset(self, setup_commit_test_data):
        """Test session behavior when deleting from an empty dataset."""
        nonexistent_app_id = str(uuid.uuid4())

        # Should not raise any errors and should return 0
        deleted_count = delete_draft_variables_batch(nonexistent_app_id, batch_size=10)
        assert deleted_count == 0

    def test_session_commit_with_single_batch(self, setup_commit_test_data):
        """Test that commit happens correctly when all data fits in a single batch."""
        data = setup_commit_test_data
        app_id = data["app"].id

        with session_factory.create_session() as session:
            initial_count = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
        assert initial_count == 10

        # Delete all in a single batch
        deleted_count = delete_draft_variables_batch(app_id, batch_size=100)
        assert deleted_count == 10

        # Verify data is persisted
        with session_factory.create_session() as session:
            final_count = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
        assert final_count == 0

    def test_invalid_batch_size_raises_error(self, setup_commit_test_data):
        """Test that invalid batch size raises ValueError."""
        data = setup_commit_test_data
        app_id = data["app"].id

        with pytest.raises(ValueError, match="batch_size must be positive"):
            delete_draft_variables_batch(app_id, batch_size=0)

        with pytest.raises(ValueError, match="batch_size must be positive"):
            delete_draft_variables_batch(app_id, batch_size=-1)

    @patch("extensions.ext_storage.storage")
    def test_session_commit_with_offload_data_cleanup(self, mock_storage, setup_offload_test_data):
        """Test that session commits correctly when cleaning up offload data."""
        data = setup_offload_test_data
        app_id = data["app"].id
        upload_file_ids = [uf.id for uf in data["upload_files"]]
        mock_storage.delete.return_value = None

        # Verify initial state
        with session_factory.create_session() as session:
            draft_vars_before = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
            var_files_before = (
                session.query(WorkflowDraftVariableFile)
                .where(WorkflowDraftVariableFile.id.in_([vf.id for vf in data["variable_files"]]))
                .count()
            )
            upload_files_before = session.query(UploadFile).where(UploadFile.id.in_(upload_file_ids)).count()
        assert draft_vars_before == 3
        assert var_files_before == 2
        assert upload_files_before == 2

        # Delete variables with offload data
        deleted_count = delete_draft_variables_batch(app_id, batch_size=10)
        assert deleted_count == 3

        # Verify all data is persisted (deleted) in new session
        with session_factory.create_session() as session:
            draft_vars_after = session.query(WorkflowDraftVariable).filter_by(app_id=app_id).count()
            var_files_after = (
                session.query(WorkflowDraftVariableFile)
                .where(WorkflowDraftVariableFile.id.in_([vf.id for vf in data["variable_files"]]))
                .count()
            )
            upload_files_after = session.query(UploadFile).where(UploadFile.id.in_(upload_file_ids)).count()
        assert draft_vars_after == 0
        assert var_files_after == 0
        assert upload_files_after == 0

        # Verify storage cleanup was called
        assert mock_storage.delete.call_count == 2
>>>>>>> upstream/main
