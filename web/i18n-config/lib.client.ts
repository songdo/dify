<<<<<<< HEAD
'use client'

import type { NamespaceCamelCase } from './resources'
import { useTranslation as useTranslationOriginal } from 'react-i18next'

export function useTranslation(ns?: NamespaceCamelCase) {
  return useTranslationOriginal(ns)
}

export { useLocale } from '@/context/i18n'
=======
'use client'

import type { Namespace } from './resources'
import { useTranslation as useTranslationOriginal } from 'react-i18next'

export function useTranslation<T extends Namespace | undefined = undefined>(ns?: T) {
  return useTranslationOriginal(ns)
}

export { useLocale } from '@/context/i18n'
>>>>>>> upstream/main
