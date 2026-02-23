<<<<<<< HEAD
import type { AccessMode } from '@/models/access-control'
import type { App, AppCategory } from '@/models/explore'
import { del, get, patch } from './base'

export const fetchAppList = () => {
  return get<{
    categories: AppCategory[]
    recommended_apps: App[]
  }>('/explore/apps')
}

export const fetchAppDetail = (id: string): Promise<any> => {
  return get(`/explore/apps/${id}`)
}

export const fetchInstalledAppList = (app_id?: string | null) => {
  return get(`/installed-apps${app_id ? `?app_id=${app_id}` : ''}`)
}

export const uninstallApp = (id: string) => {
  return del(`/installed-apps/${id}`)
}

export const updatePinStatus = (id: string, isPinned: boolean) => {
  return patch(`/installed-apps/${id}`, {
    body: {
      is_pinned: isPinned,
    },
  })
}

export const getAppAccessModeByAppId = (appId: string) => {
  return get<{ accessMode: AccessMode }>(`/enterprise/webapp/app/access-mode?appId=${appId}`)
}
=======
import type { ChatConfig } from '@/app/components/base/chat/types'
import type { ExploreAppDetailResponse } from '@/contract/console/explore'
import type { AppMeta } from '@/models/share'
import { consoleClient } from './client'

export const fetchAppList = (language?: string) => {
  if (!language)
    return consoleClient.explore.apps({})

  return consoleClient.explore.apps({
    query: { language },
  })
}

export const fetchAppDetail = async (id: string): Promise<ExploreAppDetailResponse> => {
  const response = await consoleClient.explore.appDetail({
    params: { id },
  })
  if (!response)
    throw new Error('Recommended app not found')
  return response
}

export const fetchInstalledAppList = (appId?: string | null) => {
  if (!appId)
    return consoleClient.explore.installedApps({})

  return consoleClient.explore.installedApps({
    query: { app_id: appId },
  })
}

export const uninstallApp = (id: string) => {
  return consoleClient.explore.uninstallInstalledApp({
    params: { id },
  })
}

export const updatePinStatus = (id: string, isPinned: boolean) => {
  return consoleClient.explore.updateInstalledApp({
    params: { id },
    body: {
      is_pinned: isPinned,
    },
  })
}

export const getAppAccessModeByAppId = (appId: string) => {
  return consoleClient.explore.appAccessMode({
    query: { appId },
  })
}

export const fetchInstalledAppParams = (appId: string) => {
  return consoleClient.explore.installedAppParameters({
    params: { appId },
  }) as Promise<ChatConfig>
}

export const fetchInstalledAppMeta = (appId: string) => {
  return consoleClient.explore.installedAppMeta({
    params: { appId },
  }) as Promise<AppMeta>
}

export const fetchBanners = (language?: string) => {
  if (!language)
    return consoleClient.explore.banners({})

  return consoleClient.explore.banners({
    query: { language },
  })
}
>>>>>>> upstream/main
