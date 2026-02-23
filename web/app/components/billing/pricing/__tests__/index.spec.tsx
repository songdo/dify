<<<<<<< HEAD:web/app/components/billing/pricing/index.spec.tsx
import type { Mock } from 'vitest'
import type { UsagePlanInfo } from '../type'
import { fireEvent, render, screen } from '@testing-library/react'
import { useKeyPress } from 'ahooks'
import * as React from 'react'
import { useAppContext } from '@/context/app-context'
import { useGetPricingPageLanguage } from '@/context/i18n'
import { useProviderContext } from '@/context/provider-context'
import { Plan } from '../type'
import Pricing from './index'

let mockTranslations: Record<string, string> = {}
let mockLanguage: string | null = 'en'

vi.mock('next/link', () => ({
  default: ({ children, href, className, target }: { children: React.ReactNode, href: string, className?: string, target?: string }) => (
    <a href={href} className={className} target={target} data-testid="pricing-link">
      {children}
    </a>
  ),
}))

vi.mock('ahooks', () => ({
  useKeyPress: vi.fn(),
}))

vi.mock('@/context/app-context', () => ({
  useAppContext: vi.fn(),
}))

vi.mock('@/context/provider-context', () => ({
  useProviderContext: vi.fn(),
}))

vi.mock('@/context/i18n', () => ({
  useGetPricingPageLanguage: vi.fn(),
}))

vi.mock('react-i18next', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-i18next')>()
  return {
    ...actual,
    useTranslation: () => ({
      t: (key: string, options?: { returnObjects?: boolean, ns?: string }) => {
        if (options?.returnObjects)
          return mockTranslations[key] ?? []
        if (mockTranslations[key])
          return mockTranslations[key]
        const prefix = options?.ns ? `${options.ns}.` : ''
        return `${prefix}${key}`
      },
    }),
    Trans: ({ i18nKey }: { i18nKey: string }) => <span>{i18nKey}</span>,
  }
})

const buildUsage = (): UsagePlanInfo => ({
  buildApps: 0,
  teamMembers: 0,
  annotatedResponse: 0,
  documentsUploadQuota: 0,
  apiRateLimit: 0,
  triggerEvents: 0,
  vectorSpace: 0,
})

describe('Pricing', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockTranslations = {}
    mockLanguage = 'en'
    ;(useAppContext as Mock).mockReturnValue({ isCurrentWorkspaceManager: true })
    ;(useProviderContext as Mock).mockReturnValue({
      plan: {
        type: Plan.sandbox,
        usage: buildUsage(),
        total: buildUsage(),
      },
    })
    ;(useGetPricingPageLanguage as Mock).mockImplementation(() => mockLanguage)
  })

  // Rendering behavior
  describe('Rendering', () => {
    it('should render pricing header and localized footer link', () => {
      // Arrange
      render(<Pricing onCancel={vi.fn()} />)

      // Assert
      expect(screen.getByText('billing.plansCommon.title.plans')).toBeInTheDocument()
      expect(screen.getByTestId('pricing-link')).toHaveAttribute('href', 'https://dify.ai/en/pricing#plans-and-features')
    })
  })

  // Prop-driven behavior
  describe('Props', () => {
    it('should register esc key handler and allow switching categories', () => {
      // Arrange
      const handleCancel = vi.fn()
      render(<Pricing onCancel={handleCancel} />)

      // Act
      fireEvent.click(screen.getByText('billing.plansCommon.self'))

      // Assert
      expect(useKeyPress).toHaveBeenCalledWith(['esc'], handleCancel)
      expect(screen.queryByRole('switch')).not.toBeInTheDocument()
    })
  })

  // Edge case rendering behavior
  describe('Edge Cases', () => {
    it('should fall back to default pricing URL when language is empty', () => {
      // Arrange
      mockLanguage = ''
      render(<Pricing onCancel={vi.fn()} />)

      // Assert
      expect(screen.getByTestId('pricing-link')).toHaveAttribute('href', 'https://dify.ai/pricing#plans-and-features')
    })
  })
})
=======
import type { Mock } from 'vitest'
import type { UsagePlanInfo } from '../../type'
import { fireEvent, render, screen } from '@testing-library/react'
import * as React from 'react'
import { useAppContext } from '@/context/app-context'
import { useGetPricingPageLanguage } from '@/context/i18n'
import { useProviderContext } from '@/context/provider-context'
import { Plan } from '../../type'
import Pricing from '../index'

let mockLanguage: string | null = 'en'

vi.mock('../plans/self-hosted-plan-item/list', () => ({
  default: ({ plan }: { plan: string }) => (
    <div data-testid={`list-${plan}`}>
      List for
      {plan}
    </div>
  ),
}))

vi.mock('next/link', () => ({
  default: ({ children, href, className, target }: { children: React.ReactNode, href: string, className?: string, target?: string }) => (
    <a href={href} className={className} target={target} data-testid="pricing-link">
      {children}
    </a>
  ),
}))

vi.mock('@/context/app-context', () => ({
  useAppContext: vi.fn(),
}))

vi.mock('@/context/provider-context', () => ({
  useProviderContext: vi.fn(),
}))

vi.mock('@/context/i18n', () => ({
  useGetPricingPageLanguage: vi.fn(),
}))

const buildUsage = (): UsagePlanInfo => ({
  buildApps: 0,
  teamMembers: 0,
  annotatedResponse: 0,
  documentsUploadQuota: 0,
  apiRateLimit: 0,
  triggerEvents: 0,
  vectorSpace: 0,
})

describe('Pricing', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLanguage = 'en'
    ;(useAppContext as Mock).mockReturnValue({ isCurrentWorkspaceManager: true })
    ;(useProviderContext as Mock).mockReturnValue({
      plan: {
        type: Plan.sandbox,
        usage: buildUsage(),
        total: buildUsage(),
      },
    })
    ;(useGetPricingPageLanguage as Mock).mockImplementation(() => mockLanguage)
  })

  describe('Rendering', () => {
    it('should render pricing header and localized footer link', () => {
      render(<Pricing onCancel={vi.fn()} />)

      expect(screen.getByText('billing.plansCommon.title.plans')).toBeInTheDocument()
      expect(screen.getByTestId('pricing-link')).toHaveAttribute('href', 'https://dify.ai/en/pricing#plans-and-features')
    })
  })

  describe('Props', () => {
    it('should allow switching categories and handle esc key', () => {
      const handleCancel = vi.fn()
      render(<Pricing onCancel={handleCancel} />)

      fireEvent.click(screen.getByText('billing.plansCommon.self'))
      expect(screen.queryByRole('switch')).not.toBeInTheDocument()

      fireEvent.keyDown(window, { key: 'Escape', keyCode: 27 })
      expect(handleCancel).toHaveBeenCalled()
    })
  })

  describe('Edge Cases', () => {
    it('should fall back to default pricing URL when language is empty', () => {
      mockLanguage = ''
      render(<Pricing onCancel={vi.fn()} />)

      expect(screen.getByTestId('pricing-link')).toHaveAttribute('href', 'https://dify.ai/pricing#plans-and-features')
    })
  })
})
>>>>>>> upstream/main:web/app/components/billing/pricing/__tests__/index.spec.tsx
