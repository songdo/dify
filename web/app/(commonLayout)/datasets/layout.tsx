<<<<<<< HEAD
'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Loading from '@/app/components/base/loading'
import { useAppContext } from '@/context/app-context'
import { ExternalApiPanelProvider } from '@/context/external-api-panel-context'
import { ExternalKnowledgeApiProvider } from '@/context/external-knowledge-api-context'

export default function DatasetsLayout({ children }: { children: React.ReactNode }) {
  const { isCurrentWorkspaceEditor, isCurrentWorkspaceDatasetOperator, currentWorkspace, isLoadingCurrentWorkspace } = useAppContext()
  const router = useRouter()

  useEffect(() => {
    if (isLoadingCurrentWorkspace || !currentWorkspace.id)
      return
    if (!(isCurrentWorkspaceEditor || isCurrentWorkspaceDatasetOperator))
      router.replace('/apps')
  }, [isCurrentWorkspaceEditor, isCurrentWorkspaceDatasetOperator, isLoadingCurrentWorkspace, currentWorkspace, router])

  if (isLoadingCurrentWorkspace || !(isCurrentWorkspaceEditor || isCurrentWorkspaceDatasetOperator))
    return <Loading type="app" />
  return (
    <ExternalKnowledgeApiProvider>
      <ExternalApiPanelProvider>
        {children}
      </ExternalApiPanelProvider>
    </ExternalKnowledgeApiProvider>
  )
}
=======
'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Loading from '@/app/components/base/loading'
import { useAppContext } from '@/context/app-context'
import { ExternalApiPanelProvider } from '@/context/external-api-panel-context'
import { ExternalKnowledgeApiProvider } from '@/context/external-knowledge-api-context'

export default function DatasetsLayout({ children }: { children: React.ReactNode }) {
  const { isCurrentWorkspaceEditor, isCurrentWorkspaceDatasetOperator, currentWorkspace, isLoadingCurrentWorkspace } = useAppContext()
  const router = useRouter()
  const shouldRedirect = !isLoadingCurrentWorkspace
    && currentWorkspace.id
    && !(isCurrentWorkspaceEditor || isCurrentWorkspaceDatasetOperator)

  useEffect(() => {
    if (shouldRedirect)
      router.replace('/apps')
  }, [shouldRedirect, router])

  if (isLoadingCurrentWorkspace || !currentWorkspace.id)
    return <Loading type="app" />

  if (shouldRedirect) {
    return null
  }

  return (
    <ExternalKnowledgeApiProvider>
      <ExternalApiPanelProvider>
        {children}
      </ExternalApiPanelProvider>
    </ExternalKnowledgeApiProvider>
  )
}
>>>>>>> upstream/main
