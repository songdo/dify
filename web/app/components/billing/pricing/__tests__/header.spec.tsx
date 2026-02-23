<<<<<<< HEAD:web/app/components/billing/pricing/header.spec.tsx
import { fireEvent, render, screen } from '@testing-library/react'
import * as React from 'react'
import Header from './header'

let mockTranslations: Record<string, string> = {}

vi.mock('react-i18next', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-i18next')>()
  return {
    ...actual,
    useTranslation: () => ({
      t: (key: string, options?: { ns?: string }) => {
        if (mockTranslations[key])
          return mockTranslations[key]
        const prefix = options?.ns ? `${options.ns}.` : ''
        return `${prefix}${key}`
      },
    }),
  }
})

describe('Header', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockTranslations = {}
  })

  // Rendering behavior
  describe('Rendering', () => {
    it('should render title and description translations', () => {
      // Arrange
      const handleClose = vi.fn()

      // Act
      render(<Header onClose={handleClose} />)

      // Assert
      expect(screen.getByText('billing.plansCommon.title.plans')).toBeInTheDocument()
      expect(screen.getByText('billing.plansCommon.title.description')).toBeInTheDocument()
      expect(screen.getByRole('button')).toBeInTheDocument()
    })
  })

  // Prop-driven behavior
  describe('Props', () => {
    it('should invoke onClose when close button is clicked', () => {
      // Arrange
      const handleClose = vi.fn()
      render(<Header onClose={handleClose} />)

      // Act
      fireEvent.click(screen.getByRole('button'))

      // Assert
      expect(handleClose).toHaveBeenCalledTimes(1)
    })
  })

  // Edge case rendering behavior
  describe('Edge Cases', () => {
    it('should render structure when translations are empty strings', () => {
      // Arrange
      mockTranslations = {
        'billing.plansCommon.title.plans': '',
        'billing.plansCommon.title.description': '',
      }

      // Act
      const { container } = render(<Header onClose={vi.fn()} />)

      // Assert
      expect(container.querySelector('span')).toBeInTheDocument()
      expect(container.querySelector('p')).toBeInTheDocument()
      expect(screen.getByRole('button')).toBeInTheDocument()
    })
  })
})
=======
import { fireEvent, render, screen } from '@testing-library/react'
import * as React from 'react'
import Header from '../header'

describe('Header', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render title and description translations', () => {
      const handleClose = vi.fn()

      render(<Header onClose={handleClose} />)

      expect(screen.getByText('billing.plansCommon.title.plans')).toBeInTheDocument()
      expect(screen.getByText('billing.plansCommon.title.description')).toBeInTheDocument()
      expect(screen.getByRole('button')).toBeInTheDocument()
    })
  })

  describe('Props', () => {
    it('should invoke onClose when close button is clicked', () => {
      const handleClose = vi.fn()
      render(<Header onClose={handleClose} />)

      fireEvent.click(screen.getByRole('button'))

      expect(handleClose).toHaveBeenCalledTimes(1)
    })
  })

  describe('Edge Cases', () => {
    it('should render structural elements with translation keys', () => {
      const { container } = render(<Header onClose={vi.fn()} />)

      expect(container.querySelector('span')).toBeInTheDocument()
      expect(container.querySelector('p')).toBeInTheDocument()
      expect(screen.getByRole('button')).toBeInTheDocument()
    })
  })
})
>>>>>>> upstream/main:web/app/components/billing/pricing/__tests__/header.spec.tsx
