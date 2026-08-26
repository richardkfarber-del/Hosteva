import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';

describe('ProtectedRoute', () => {
  it('redirects to pricing if not premium', () => {
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route 
            path="/protected" 
            element={
              <ProtectedRoute isPremium={false}>
                <div>Premium Content</div>
              </ProtectedRoute>
            } 
          />
          <Route path="/pricing" element={<div>Pricing Page</div>} />
        </Routes>
      </MemoryRouter>
    );
    
    expect(screen.getByText('Pricing Page')).toBeInTheDocument();
    expect(screen.queryByText('Premium Content')).not.toBeInTheDocument();
  });

  it('renders children if premium', () => {
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route 
            path="/protected" 
            element={
              <ProtectedRoute isPremium={true}>
                <div>Premium Content</div>
              </ProtectedRoute>
            } 
          />
          <Route path="/pricing" element={<div>Pricing Page</div>} />
        </Routes>
      </MemoryRouter>
    );
    
    expect(screen.getByText('Premium Content')).toBeInTheDocument();
    expect(screen.queryByText('Pricing Page')).not.toBeInTheDocument();
  });
});
