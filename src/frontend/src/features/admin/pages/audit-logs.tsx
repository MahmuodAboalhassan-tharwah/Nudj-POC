import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuditLogs, useExportAuditLogs } from '@/features/admin/api/admin.api';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Download, Loader2 } from 'lucide-react';
import { format } from 'date-fns';

export const AuditLogsPage = () => {
    const { t } = useTranslation();
    const [page, setPage] = useState(1);

    const { data, isLoading } = useAuditLogs({
        page,
        pageSize: 20,
    });

    const { mutate: exportLogs, isPending: isExporting } = useExportAuditLogs();

    return (
        <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{t('admin.audit.title', 'Audit Logs')}</h1>
                    <p className="text-muted-foreground">
                        {t('admin.audit.subtitle', 'Track system activities and security events')}
                    </p>
                </div>
                <Button variant="outline" onClick={() => exportLogs({})} disabled={isExporting}>
                    {isExporting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
                    {t('common.export', 'Export CSV')}
                </Button>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>{t('common.date', 'Date')}</TableHead>
                            <TableHead>{t('common.user', 'User')}</TableHead>
                            <TableHead>{t('common.action', 'Action')}</TableHead>
                            <TableHead>{t('common.resource', 'Resource')}</TableHead>
                            <TableHead>{t('common.details', 'Details')}</TableHead>
                            <TableHead>{t('common.ip', 'IP Address')}</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            <TableRow>
                                <TableCell colSpan={6} className="h-24 text-center">
                                    <Loader2 className="mx-auto h-6 w-6 animate-spin text-muted-foreground" />
                                </TableCell>
                            </TableRow>
                        ) : data?.items.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                                    {t('common.noResults', 'No logs found')}
                                </TableCell>
                            </TableRow>
                        ) : (
                            data?.items.map((log) => (
                                <TableRow key={log.id}>
                                    <TableCell className="whitespace-nowrap">
                                        {format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                                    </TableCell>
                                    <TableCell>{log.user_email || 'System'}</TableCell>
                                    <TableCell className="font-medium">{log.action}</TableCell>
                                    <TableCell>{log.resource_type}</TableCell>
                                    <TableCell className="max-w-[200px] truncate" title={JSON.stringify(log.details)}>
                                        {JSON.stringify(log.details)}
                                    </TableCell>
                                    <TableCell>{log.ip_address}</TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
            
             {/* Pagination Controls would go here */}
        </div>
    );
};
