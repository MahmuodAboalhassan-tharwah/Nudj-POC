import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useUsers, useInviteUser, useDeactivateUser } from '@/features/admin/api/admin.api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Loader2, MoreHorizontal, Plus, Search } from 'lucide-react';
import { InviteUserDialog } from './invite-user-dialog'; // create this next

export const UsersListPage = () => {
    const { t } = useTranslation();
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const [isInviteOpen, setIsInviteOpen] = useState(false);

    const { data, isLoading } = useUsers({
        page,
        pageSize: 10,
        search,
    });

    const { mutate: deactivateUser } = useDeactivateUser();

    const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(e.target.value);
        setPage(1); // Reset to first page
    };

    return (
        <div className="p-8 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{t('admin.users.title', 'Users')}</h1>
                    <p className="text-muted-foreground">
                        {t('admin.users.subtitle', 'Manage users and invitations')}
                    </p>
                </div>
                <Button onClick={() => setIsInviteOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    {t('admin.users.invite', 'Invite User')}
                </Button>
            </div>

            <div className="flex items-center space-x-2">
                <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder={t('common.search', 'Search users...')}
                        value={search}
                        onChange={handleSearch}
                        className="pl-8"
                    />
                </div>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>{t('common.name', 'Name')}</TableHead>
                            <TableHead>{t('common.email', 'Email')}</TableHead>
                            <TableHead>{t('common.role', 'Role')}</TableHead>
                            <TableHead>{t('common.status', 'Status')}</TableHead>
                            <TableHead className="text-right">{t('common.actions', 'Actions')}</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            <TableRow>
                                <TableCell colSpan={5} className="h-24 text-center">
                                    <Loader2 className="mx-auto h-6 w-6 animate-spin text-muted-foreground" />
                                </TableCell>
                            </TableRow>
                        ) : data?.items.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                                    {t('common.noResults', 'No users found')}
                                </TableCell>
                            </TableRow>
                        ) : (
                            data?.items.map((user) => (
                                <TableRow key={user.id}>
                                    <TableCell className="font-medium">
                                        {user.name_en} / {user.name_ar}
                                    </TableCell>
                                    <TableCell>{user.email}</TableCell>
                                    <TableCell>
                                        <Badge variant="outline">{user.role}</Badge>
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant={user.is_active ? 'default' : 'destructive'}>
                                            {user.is_active ? 'Active' : 'Inactive'}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button variant="ghost" className="h-8 w-8 p-0">
                                                    <span className="sr-only">Open menu</span>
                                                    <MoreHorizontal className="h-4 w-4" />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                                <DropdownMenuItem onClick={() => navigator.clipboard.writeText(user.id)}>
                                                    Copy ID
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => console.log('Edit', user.id)}>
                                                    Edit User
                                                </DropdownMenuItem>
                                                <DropdownMenuItem 
                                                    className="text-destructive focus:text-destructive"
                                                    onClick={() => deactivateUser(user.id)}
                                                >
                                                    Deactivate
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Pagination Controls would go here */}

            <InviteUserDialog open={isInviteOpen} onOpenChange={setIsInviteOpen} />
        </div>
    );
};
