<<<<<<< HEAD:web/app/components/share/text-generation/no-data/index.spec.tsx
import { render, screen } from '@testing-library/react'
import * as React from 'react'
import NoData from './index'

describe('NoData', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  it('should render empty state icon and text when mounted', () => {
    const { container } = render(<NoData />)

    expect(container.querySelector('svg')).toBeInTheDocument()
    expect(screen.getByText('share.generation.noData')).toBeInTheDocument()
  })
})
=======
import { render, screen } from '@testing-library/react'
import * as React from 'react'
import NoData from '../index'

describe('NoData', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  it('should render empty state icon and text when mounted', () => {
    const { container } = render(<NoData />)

    expect(container.querySelector('svg')).toBeInTheDocument()
    expect(screen.getByText('share.generation.noData')).toBeInTheDocument()
  })
})
>>>>>>> upstream/main:web/app/components/share/text-generation/no-data/__tests__/index.spec.tsx
