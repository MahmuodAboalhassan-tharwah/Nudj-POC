import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { toast } from 'sonner';
import { Users, Shield, BookOpen, AlertCircle, Loader2, Plus, X } from 'lucide-react';
import { useCreateDelegation, useDelegations, useRevokeDelegation } from '../api/assessments.api';
import { useUsers } from '@/features/admin/api/admin.api';
import { AssessmentDomain } from '../types/assessment.types';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { useTranslation } from 'react-i18next';

interface DelegationDialogProps {
  assessmentId: string;
  organizationId: string;
  domains: AssessmentDomain[];
  children?: React.ReactNode;
}

export const DelegationDialog = ({ assessmentId, organizationId, domains, children }: DelegationDialogProps) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  const delegationSchema = z.object({
    userId: z.string().min(1, t('assessments.delegation.validation.selectUser')),
    domainId: z.string().optional(),
    notes: z.string().max(500, t('assessments.delegation.validation.notesTooLong')).optional(),
  });

  type DelegationFormValues = z.infer<typeof delegationSchema>;

  const { data: usersData, isLoading: isLoadingUsers } = useUsers({ 
    page: 1, 
    pageSize: 100, 
    organization_id: organizationId 
  });
  
  const { data: delegations, isLoading: isLoadingDelegations } = useDelegations(assessmentId);
  const { mutate: create, isPending: isCreating } = useCreateDelegation();
  const { mutate: revoke } = useRevokeDelegation();

  const form = useForm<DelegationFormValues>({
    resolver: zodResolver(delegationSchema),
    defaultValues: {
      userId: '',
      domainId: 'whole', // special value for whole assessment
      notes: '',
    }
  });

  const onSubmit = (values: DelegationFormValues) => {
    create({
      assessmentId,
      userId: values.userId,
      domainId: values.domainId === 'whole' ? undefined : values.domainId,
      notes: values.notes,
    }, {
      onSuccess: () => {
        toast.success(t('assessments.delegation.success'));
        form.reset({
            userId: '',
            domainId: 'whole',
            notes: '',
        });
      },
      onError: () => {
        toast.error(t('assessments.delegation.error'));
      }
    });
  };

  const handleRevoke = (id: string) => {
      revoke(id, {
          onSuccess: () => toast.success(t('assessments.delegation.revokeSuccess')),
          onError: () => toast.error(t('assessments.delegation.revokeError'))
      });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button variant="outline" className="gap-2">
            <Users className="w-4 h-4" />
            {t('assessments.delegation.title')}
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px] gap-0 p-0 overflow-hidden bg-white text-slate-900">
        <div className="p-6 pb-4 border-b bg-slate-50/50">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl font-bold text-slate-900">
              <Shield className="w-5 h-5 text-primary" />
              {t('assessments.delegation.title')}
            </DialogTitle>
            <DialogDescription className="text-slate-500">
              {t('assessments.delegation.description')}
            </DialogDescription>
          </DialogHeader>
        </div>

        <div className="flex flex-col h-[500px]">
          <div className="p-6 border-b">
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="userId"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t('assessments.delegation.teamMember')}</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger className="bg-white border-slate-200 focus:ring-primary/20">
                              <SelectValue placeholder={t('assessments.delegation.selectUser')} />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {isLoadingUsers ? (
                                <div className="p-2 space-y-2">
                                    <Skeleton className="h-8 w-full" />
                                    <Skeleton className="h-8 w-full" />
                                </div>
                            ) : (
                                usersData?.items.map((user) => (
                                    <SelectItem key={user.id} value={user.id}>
                                      {user.name_en || user.email}
                                    </SelectItem>
                                ))
                            )}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="domainId"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t('assessments.delegation.scope')}</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger className="bg-white border-slate-200 focus:ring-primary/20">
                              <SelectValue placeholder={t('assessments.delegation.selectScope')} />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="whole">{t('assessments.delegation.wholeAssessment')}</SelectItem>
                            {domains.map((domain) => (
                              <SelectItem key={domain.id} value={domain.id}>
                                {t('assessments.delegation.domainPrefix')} {domain.domainId}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="notes"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t('assessments.delegation.notes')}</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder={t('assessments.delegation.notesPlaceholder')} 
                          className="resize-none bg-white border-slate-200 focus:ring-primary/20"
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button type="submit" className="w-full shadow-lg shadow-primary/20" disabled={isCreating}>
                  {isCreating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {t('assessments.delegation.delegating')}
                    </>
                  ) : (
                    <>
                      <Plus className="mr-2 h-4 w-4" />
                      {t('assessments.delegation.assignTask')}
                    </>
                  )}
                </Button>
              </form>
            </Form>
          </div>

          <div className="flex-1 min-h-0 bg-slate-50/30">
            <div className="p-4 px-6 border-b bg-white/50 sticky top-0 z-10">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">{t('assessments.delegation.currentAssignments')}</h3>
            </div>
            <ScrollArea className="h-full">
              <div className="p-6 py-4 space-y-3">
                {isLoadingDelegations ? (
                  <div className="space-y-3">
                    <Skeleton className="h-16 w-full rounded-xl" />
                    <Skeleton className="h-16 w-full rounded-xl" />
                  </div>
                ) : delegations?.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-center bg-white rounded-2xl border border-dashed border-slate-200">
                    <AlertCircle className="w-8 h-8 text-slate-300 mb-2" />
                    <p className="text-sm text-slate-500">{t('assessments.delegation.noDelegations')}</p>
                  </div>
                ) : (
                  delegations?.map((delegation) => (
                    <div 
                      key={delegation.id} 
                      className="group flex items-start justify-between p-4 bg-white rounded-xl border border-slate-200 hover:border-primary/30 transition-all hover:shadow-md hover:shadow-slate-200/50"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-900">{delegation.delegateeName || t('assessments.delegation.user')}</span>
                          <Badge variant="secondary" className="bg-slate-100 text-slate-600 border-none font-medium text-[10px] h-5">
                            {delegation.domainName || t('assessments.delegation.assessment')}
                          </Badge>
                        </div>
                        {delegation.notes && (
                            <p className="text-xs text-slate-500 line-clamp-1 italic">"{delegation.notes}"</p>
                        )}
                        <p className="text-[10px] text-slate-400">
                          {t('assessments.delegation.assignedOn')} {new Date(delegation.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        onClick={() => handleRevoke(delegation.id)}
                        className="opacity-0 group-hover:opacity-100 h-8 w-8 text-slate-400 hover:text-destructive hover:bg-destructive/10 transition-all"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
