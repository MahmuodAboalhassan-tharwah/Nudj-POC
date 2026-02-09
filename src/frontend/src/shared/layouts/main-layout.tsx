import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { useLogout } from '@/features/auth/api/auth.api';
import { NotificationCenter } from '@/features/notifications/components/notification-center';
import { LanguageSwitcher } from '@/shared/components/language-switcher';
import { useTranslation } from 'react-i18next';

export const MainLayout = () => {
    const { user, isSuperAdmin } = useAuth();
    const { mutate: logout } = useLogout();
    const { t } = useTranslation();

    return (
        <div className="min-h-screen flex flex-col bg-slate-50/50">
            <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-md px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-8">
                    <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                            <span className="text-primary-foreground font-bold italic">N</span>
                        </div>
                        <h1 className="text-xl font-bold tracking-tight">Nudj</h1>
                    </div>
                    <nav className="hidden md:flex gap-6">
                        <Link to="/dashboard" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">{t('common.dashboard')}</Link>
                        {(isSuperAdmin || user?.role === 'client_admin') && (
                            <Link to="/admin/users" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">{t('common.users')}</Link>
                        )}
                        {isSuperAdmin && (
                            <Link to="/admin/audit-logs" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">{t('common.auditLogs')}</Link>
                        )}
                        {isSuperAdmin && (
                            <Link to="/admin/organizations" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">{t('common.organizations')}</Link>
                        )}
                    </nav>
                </div>
                <div className="flex items-center gap-4">
                    <LanguageSwitcher />
                    <div className="flex items-center gap-3 pr-4 border-r ltr:border-r rtl:border-l rtl:pr-0 rtl:pl-4">
                        <NotificationCenter />
                        <div className="flex flex-col items-end rtl:items-start text-right rtl:text-left">
                            <span className="text-sm font-medium leading-none">{user?.email?.split('@')[0]}</span>
                            <span className="text-[10px] text-muted-foreground uppercase tracking-widest">{user?.role?.replace('_', ' ')}</span>
                        </div>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => logout()} className="text-muted-foreground hover:text-destructive transition-colors">
                        {t('common.logout')}
                    </Button>
                </div>
            </header>
            <main className="flex-1">
                <div className="container mx-auto py-8 px-4 md:px-6">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};
