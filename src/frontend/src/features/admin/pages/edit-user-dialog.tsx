import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslation } from 'react-i18next';
import { useUpdateUser, useUser } from '@/features/admin/api/admin.api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import { Switch } from '@/components/ui/switch';

const editUserSchema = z.object({
  name_en: z.string().min(2, 'Name (English) is required'),
  name_ar: z.string().min(2, 'Name (Arabic) is required'),
  role: z.string().min(1, 'Role is required'),
  is_active: z.boolean(),
});

type EditUserFormData = z.infer<typeof editUserSchema>;

interface EditUserDialogProps {
  userId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const EditUserDialog = ({ userId, open, onOpenChange }: EditUserDialogProps) => {
  const { t } = useTranslation();
  const { data: user, isLoading: isLoadingUser } = useUser(userId || '');
  const { mutate: updateUser, isPending: isUpdating } = useUpdateUser();
  
  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<EditUserFormData>({
    resolver: zodResolver(editUserSchema),
    defaultValues: {
        name_en: '',
        name_ar: '',
        role: '',
        is_active: true,
    },
  });

  useEffect(() => {
    if (user) {
        setValue('name_en', user.name_en);
        setValue('name_ar', user.name_ar);
        setValue('role', user.role);
        setValue('is_active', user.is_active);
    }
  }, [user, setValue]);

  const onSubmit = (data: EditUserFormData) => {
    if (!userId) return;
    
    updateUser(
      {
        userId,
        data: {
            name_en: data.name_en,
            name_ar: data.name_ar,
            role: data.role as any,
            is_active: data.is_active,
        }
      },
      {
        onSuccess: () => {
          onOpenChange(false);
          reset();
        },
      }
    );
  };

  if (!userId) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{t('admin.users.editTitle', 'Edit User')}</DialogTitle>
          <DialogDescription>
            {t('admin.users.editDescription', 'Update user details and role.')}
          </DialogDescription>
        </DialogHeader>
        
        {isLoadingUser ? (
             <div className="flex justify-center p-4">
                <Loader2 className="h-6 w-6 animate-spin" />
             </div>
        ) : (
            <form onSubmit={handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <Label htmlFor="name_en">{t('common.nameEn', 'Name (EN)')}</Label>
                        <Input id="name_en" {...register('name_en')} />
                        {errors.name_en && <p className="text-sm text-destructive">{errors.name_en.message}</p>}
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="name_ar">{t('common.nameAr', 'Name (AR)')}</Label>
                        <Input id="name_ar" {...register('name_ar')} dir="rtl" />
                        {errors.name_ar && <p className="text-sm text-destructive">{errors.name_ar.message}</p>}
                    </div>
                </div>
                
                <div className="space-y-2">
                <Label htmlFor="edit-role">{t('common.role', 'Role')}</Label>
                <Select 
                    onValueChange={(val) => setValue('role', val)} 
                    defaultValue={user?.role}
                >
                    <SelectTrigger id="edit-role">
                    <SelectValue placeholder="Select a role" />
                    </SelectTrigger>
                    <SelectContent>
                    <SelectItem value="super_admin">Super Admin</SelectItem>
                    <SelectItem value="analyst">Analyst</SelectItem>
                    <SelectItem value="client_admin">Client Admin</SelectItem>
                    <SelectItem value="assessor">Assessor</SelectItem>
                    </SelectContent>
                </Select>
                {errors.role && <p className="text-sm text-destructive">{errors.role.message}</p>}
                </div>

                <div className="flex items-center space-x-2">
                    <Switch 
                        id="is_active" 
                        checked={user?.is_active}
                        onCheckedChange={(checked) => setValue('is_active', checked)}
                    />
                    <Label htmlFor="is_active">{t('common.active', 'Active Account')}</Label>
                </div>
            </div>
            <DialogFooter>
                <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                    Cancel
                </Button>
                <Button type="submit" disabled={isUpdating}>
                {isUpdating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {t('common.save', 'Save Changes')}
                </Button>
            </DialogFooter>
            </form>
        )}
      </DialogContent>
    </Dialog>
  );
};
