// Button.test.js
import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button Component', () => {
  it('should render with label and call onClick on click', () => {
    const handleClick = jest.fn();

    const { getByText } = render(<Button label="Click Me" onClick={handleClick} />);

    fireEvent.click(getByText('Click Me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
