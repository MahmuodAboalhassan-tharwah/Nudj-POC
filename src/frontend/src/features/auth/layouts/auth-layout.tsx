import { Outlet } from 'react-router-dom';

export const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-muted/40">
      <Outlet />
    </div>
  );
};
