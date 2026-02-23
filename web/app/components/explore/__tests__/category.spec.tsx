<<<<<<< HEAD:web/app/components/explore/category.spec.tsx
import type { AppCategory } from '@/models/explore'
import { fireEvent, render, screen } from '@testing-library/react'
import Category from './category'

describe('Category', () => {
  const allCategoriesEn = 'Recommended'

  const renderComponent = (overrides: Partial<React.ComponentProps<typeof Category>> = {}) => {
    const props: React.ComponentProps<typeof Category> = {
      list: ['Writing', 'Recommended'] as AppCategory[],
      value: allCategoriesEn,
      onChange: vi.fn(),
      allCategoriesEn,
      ...overrides,
    }
    return {
      props,
      ...render(<Category {...props} />),
    }
  }

  // Rendering: basic categories and all-categories button.
  describe('Rendering', () => {
    it('should render all categories item and translated categories', () => {
      // Arrange
      renderComponent()

      // Assert
      expect(screen.getByText('explore.apps.allCategories')).toBeInTheDocument()
      expect(screen.getByText('explore.category.Writing')).toBeInTheDocument()
    })

    it('should not render allCategoriesEn again inside the category list', () => {
      // Arrange
      renderComponent()

      // Assert
      const recommendedItems = screen.getAllByText('explore.apps.allCategories')
      expect(recommendedItems).toHaveLength(1)
    })
  })

  // Props: clicking items triggers onChange.
  describe('Props', () => {
    it('should call onChange with category value when category item is clicked', () => {
      // Arrange
      const { props } = renderComponent()

      // Act
      fireEvent.click(screen.getByText('explore.category.Writing'))

      // Assert
      expect(props.onChange).toHaveBeenCalledWith('Writing')
    })

    it('should call onChange with allCategoriesEn when all categories is clicked', () => {
      // Arrange
      const { props } = renderComponent({ value: 'Writing' })

      // Act
      fireEvent.click(screen.getByText('explore.apps.allCategories'))

      // Assert
      expect(props.onChange).toHaveBeenCalledWith(allCategoriesEn)
    })
  })

  // Edge cases: handle values not in the list.
  describe('Edge Cases', () => {
    it('should treat unknown value as all categories selection', () => {
      // Arrange
      renderComponent({ value: 'Unknown' })

      // Assert
      const allCategoriesItem = screen.getByText('explore.apps.allCategories')
      expect(allCategoriesItem.className).toContain('bg-components-main-nav-nav-button-bg-active')
    })
  })
})
=======
import type { AppCategory } from '@/models/explore'
import { fireEvent, render, screen } from '@testing-library/react'
import Category from '../category'

describe('Category', () => {
  const allCategoriesEn = 'Recommended'

  const renderComponent = (overrides: Partial<React.ComponentProps<typeof Category>> = {}) => {
    const props: React.ComponentProps<typeof Category> = {
      list: ['Writing', 'Recommended'] as AppCategory[],
      value: allCategoriesEn,
      onChange: vi.fn(),
      allCategoriesEn,
      ...overrides,
    }
    return {
      props,
      ...render(<Category {...props} />),
    }
  }

  describe('Rendering', () => {
    it('should render all categories item and translated categories', () => {
      renderComponent()

      expect(screen.getByText('explore.apps.allCategories')).toBeInTheDocument()
      expect(screen.getByText('explore.category.Writing')).toBeInTheDocument()
    })

    it('should not render allCategoriesEn again inside the category list', () => {
      renderComponent()

      const recommendedItems = screen.getAllByText('explore.apps.allCategories')
      expect(recommendedItems).toHaveLength(1)
    })
  })

  describe('Props', () => {
    it('should call onChange with category value when category item is clicked', () => {
      const { props } = renderComponent()

      fireEvent.click(screen.getByText('explore.category.Writing'))

      expect(props.onChange).toHaveBeenCalledWith('Writing')
    })

    it('should call onChange with allCategoriesEn when all categories is clicked', () => {
      const { props } = renderComponent({ value: 'Writing' })

      fireEvent.click(screen.getByText('explore.apps.allCategories'))

      expect(props.onChange).toHaveBeenCalledWith(allCategoriesEn)
    })
  })

  describe('Edge Cases', () => {
    it('should treat unknown value as all categories selection', () => {
      renderComponent({ value: 'Unknown' })

      const allCategoriesItem = screen.getByText('explore.apps.allCategories')
      expect(allCategoriesItem.className).toContain('bg-components-main-nav-nav-button-bg-active')
    })

    it('should render raw category name when i18n key does not exist', () => {
      renderComponent({ list: ['CustomCategory', 'Recommended'] as AppCategory[] })

      expect(screen.getByText('CustomCategory')).toBeInTheDocument()
    })
  })
})
>>>>>>> upstream/main:web/app/components/explore/__tests__/category.spec.tsx
