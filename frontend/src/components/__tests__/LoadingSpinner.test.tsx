import { render, screen } from '@testing-library/react'
import LoadingSpinner from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders loading spinner with three dots', () => {
    const { container } = render(<LoadingSpinner />)

    // Should render 3 animated dots
    const dots = container.querySelectorAll('.animate-bounce')
    expect(dots).toHaveLength(3)
  })

  it('renders dots with correct styling', () => {
    const { container } = render(<LoadingSpinner />)

    const dots = container.querySelectorAll('.w-2.h-2.bg-blue-500.rounded-full')
    expect(dots).toHaveLength(3)
  })

  it('applies animation delays to dots', () => {
    const { container } = render(<LoadingSpinner />)

    const dots = container.querySelectorAll('.animate-bounce')

    // First dot has no delay (default)
    expect(dots[0]).not.toHaveStyle('animation-delay: 0.1s')

    // Second dot has 0.1s delay
    expect(dots[1]).toHaveStyle('animation-delay: 0.1s')

    // Third dot has 0.2s delay
    expect(dots[2]).toHaveStyle('animation-delay: 0.2s')
  })

  it('renders with proper flex container', () => {
    const { container } = render(<LoadingSpinner />)

    const flexContainer = container.firstChild
    expect(flexContainer).toHaveClass('flex', 'items-center', 'space-x-2')
  })
})
