<<<<<<< HEAD:web/app/components/billing/priority-label/index.spec.tsx
import type { Mock } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { createMockPlan } from '@/__mocks__/provider-context'
import { useProviderContext } from '@/context/provider-context'
import { Plan } from '../type'
import PriorityLabel from './index'

vi.mock('@/context/provider-context', () => ({
  useProviderContext: vi.fn(),
}))

const useProviderContextMock = useProviderContext as Mock

const setupPlan = (planType: Plan) => {
  useProviderContextMock.mockReturnValue(createMockPlan(planType))
}

describe('PriorityLabel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Rendering: basic label output for sandbox plan.
  describe('Rendering', () => {
    it('should render the standard priority label when plan is sandbox', () => {
      // Arrange
      setupPlan(Plan.sandbox)

      // Act
      render(<PriorityLabel />)

      // Assert
      expect(screen.getByText('billing.plansCommon.priority.standard')).toBeInTheDocument()
    })
  })

  // Props: custom class name applied to the label container.
  describe('Props', () => {
    it('should apply custom className to the label container', () => {
      // Arrange
      setupPlan(Plan.sandbox)

      // Act
      render(<PriorityLabel className="custom-class" />)

      // Assert
      const label = screen.getByText('billing.plansCommon.priority.standard').closest('div')
      expect(label).toHaveClass('custom-class')
    })
  })

  // Plan types: label text and icon visibility for different plans.
  describe('Plan Types', () => {
    it('should render priority label and icon when plan is professional', () => {
      // Arrange
      setupPlan(Plan.professional)

      // Act
      const { container } = render(<PriorityLabel />)

      // Assert
      expect(screen.getByText('billing.plansCommon.priority.priority')).toBeInTheDocument()
      expect(container.querySelector('svg')).toBeInTheDocument()
    })

    it('should render top priority label and icon when plan is team', () => {
      // Arrange
      setupPlan(Plan.team)

      // Act
      const { container } = render(<PriorityLabel />)

      // Assert
      expect(screen.getByText('billing.plansCommon.priority.top-priority')).toBeInTheDocument()
      expect(container.querySelector('svg')).toBeInTheDocument()
    })

    it('should render standard label without icon when plan is sandbox', () => {
      // Arrange
      setupPlan(Plan.sandbox)

      // Act
      const { container } = render(<PriorityLabel />)

      // Assert
      expect(screen.getByText('billing.plansCommon.priority.standard')).toBeInTheDocument()
      expect(container.querySelector('svg')).not.toBeInTheDocument()
    })
  })

  // Edge cases: tooltip content varies by priority level.
  describe('Edge Cases', () => {
    it('should show the tip text when priority is not top priority', async () => {
      // Arrange
      setupPlan(Plan.sandbox)

      // Act
      render(<PriorityLabel />)
      const label = screen.getByText('billing.plansCommon.priority.standard').closest('div')
      fireEvent.mouseEnter(label as HTMLElement)

      // Assert
      expect(await screen.findByText(
        'billing.plansCommon.documentProcessingPriority: billing.plansCommon.priority.standard',
      )).toBeInTheDocument()
      expect(screen.getByText('billing.plansCommon.documentProcessingPriorityTip')).toBeInTheDocument()
    })

    it('should hide the tip text when priority is top priority', async () => {
      // Arrange
      setupPlan(Plan.enterprise)

      // Act
      render(<PriorityLabel />)
      const label = screen.getByText('billing.plansCommon.priority.top-priority').closest('div')
      fireEvent.mouseEnter(label as HTMLElement)

      // Assert
      expect(await screen.findByText(
        'billing.plansCommon.documentProcessingPriority: billing.plansCommon.priority.top-priority',
      )).toBeInTheDocument()
      expect(screen.queryByText('billing.plansCommon.documentProcessingPriorityTip')).not.toBeInTheDocument()
    })
  })
})
=======
import type { Mock } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { createMockPlan } from '@/__mocks__/provider-context'
import { useProviderContext } from '@/context/provider-context'
import { Plan } from '../../type'
import PriorityLabel from '../index'

vi.mock('@/context/provider-context', () => ({
  useProviderContext: vi.fn(),
}))

const useProviderContextMock = useProviderContext as Mock

const setupPlan = (planType: Plan) => {
  useProviderContextMock.mockReturnValue(createMockPlan(planType))
}

describe('PriorityLabel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render the standard priority label when plan is sandbox', () => {
      setupPlan(Plan.sandbox)

      render(<PriorityLabel />)

      expect(screen.getByText('billing.plansCommon.priority.standard')).toBeInTheDocument()
    })
  })

  // Props: custom class name applied to the label container.
  describe('Props', () => {
    it('should apply custom className to the label container', () => {
      setupPlan(Plan.sandbox)

      render(<PriorityLabel className="custom-class" />)

      const label = screen.getByText('billing.plansCommon.priority.standard').closest('div')
      expect(label).toHaveClass('custom-class')
    })
  })

  // Plan types: label text and icon visibility for different plans.
  describe('Plan Types', () => {
    it('should render priority label and icon when plan is professional', () => {
      setupPlan(Plan.professional)

      const { container } = render(<PriorityLabel />)

      expect(screen.getByText('billing.plansCommon.priority.priority')).toBeInTheDocument()
      expect(container.querySelector('svg')).toBeInTheDocument()
    })

    it('should render top priority label and icon when plan is team', () => {
      setupPlan(Plan.team)

      const { container } = render(<PriorityLabel />)

      expect(screen.getByText('billing.plansCommon.priority.top-priority')).toBeInTheDocument()
      expect(container.querySelector('svg')).toBeInTheDocument()
    })

    it('should render standard label without icon when plan is sandbox', () => {
      setupPlan(Plan.sandbox)

      const { container } = render(<PriorityLabel />)

      expect(screen.getByText('billing.plansCommon.priority.standard')).toBeInTheDocument()
      expect(container.querySelector('svg')).not.toBeInTheDocument()
    })
  })

  // Enterprise plan tests
  describe('Enterprise Plan', () => {
    it('should render top-priority label with icon for enterprise plan', () => {
      setupPlan(Plan.enterprise)

      const { container } = render(<PriorityLabel />)

      expect(screen.getByText('billing.plansCommon.priority.top-priority')).toBeInTheDocument()
      expect(container.querySelector('svg')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should show the tip text when priority is not top priority', async () => {
      setupPlan(Plan.sandbox)

      render(<PriorityLabel />)
      const label = screen.getByText('billing.plansCommon.priority.standard').closest('div')
      fireEvent.mouseEnter(label as HTMLElement)

      expect(await screen.findByText(
        'billing.plansCommon.documentProcessingPriority: billing.plansCommon.priority.standard',
      )).toBeInTheDocument()
      expect(screen.getByText('billing.plansCommon.documentProcessingPriorityTip')).toBeInTheDocument()
    })

    it('should hide the tip text when priority is top priority', async () => {
      setupPlan(Plan.enterprise)

      render(<PriorityLabel />)
      const label = screen.getByText('billing.plansCommon.priority.top-priority').closest('div')
      fireEvent.mouseEnter(label as HTMLElement)

      expect(await screen.findByText(
        'billing.plansCommon.documentProcessingPriority: billing.plansCommon.priority.top-priority',
      )).toBeInTheDocument()
      expect(screen.queryByText('billing.plansCommon.documentProcessingPriorityTip')).not.toBeInTheDocument()
    })
  })
})
>>>>>>> upstream/main:web/app/components/billing/priority-label/__tests__/index.spec.tsx
