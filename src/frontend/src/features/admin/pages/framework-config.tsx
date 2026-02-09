import { useTranslation } from 'react-i18next';
import { useFrameworkDomains, useUpdateDomainWeight } from '../api/framework.api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Loader2, Save } from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';

export const FrameworkConfigPage = () => {
  const { t, i18n } = useTranslation();
  const { data: domains, isLoading } = useFrameworkDomains();
  const { mutate: updateWeight, isPending } = useUpdateDomainWeight();
  
  // Local state to handle inputs before saving
  const [weights, setWeights] = useState<Record<number, number>>({});
  const [dirty, setDirty] = useState<Record<number, boolean>>({});

  useEffect(() => {
    if (domains) {
      const initialWeights: Record<number, number> = {};
      domains.forEach(d => {
        initialWeights[d.domain_id] = d.default_weight;
      });
      setWeights(initialWeights);
    }
  }, [domains]);

  const handleWeightChange = (domainId: number, value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue >= 0) {
      setWeights(prev => ({ ...prev, [domainId]: numValue }));
      setDirty(prev => ({ ...prev, [domainId]: true }));
    }
  };

  const handleSave = (domainId: number) => {
    const weight = weights[domainId];
    if (weight === undefined) return;

    updateWeight({ domainId, data: { default_weight: weight } }, {
      onSuccess: () => {
        toast.success(t('admin.framework.successUpdate'));
        setDirty(prev => ({ ...prev, [domainId]: false }));
      },
      onError: () => {
        toast.error(t('admin.framework.errorUpdate'));
      }
    });
  };

  if (isLoading) {
    return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
            {t('admin.framework.title')}
          </h1>
          <p className="text-muted-foreground mt-2">
            {t('admin.framework.description')}
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('admin.framework.domainsTitle')}</CardTitle>
          <CardDescription>{t('admin.framework.domainsDescription')}</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('admin.framework.domainId')}</TableHead>
                <TableHead>{t('admin.framework.domainName')}</TableHead>
                <TableHead>{t('admin.framework.weight')}</TableHead>
                <TableHead className="w-[100px]">{t('common.actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {domains?.map((domain) => (
                <TableRow key={domain.id}>
                  <TableCell className="font-medium">#{domain.domain_id}</TableCell>
                  <TableCell>
                    {i18n.language === 'ar' ? domain.name_ar : domain.name_en}
                  </TableCell>
                  <TableCell>
                    <div className="max-w-[120px]">
                      <Input
                        type="number"
                        step="0.1"
                        min="0"
                        value={weights[domain.domain_id] ?? domain.default_weight}
                        onChange={(e) => handleWeightChange(domain.domain_id, e.target.value)}
                        className="text-right tabular-nums"
                      />
                    </div>
                  </TableCell>
                  <TableCell>
                    {dirty[domain.domain_id] && (
                      <Button 
                        size="sm" 
                        onClick={() => handleSave(domain.domain_id)}
                        disabled={isPending}
                        className="transition-all"
                      >
                        <Save className="h-4 w-4" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
      {/* Total Weight Indicator - Optional but helpful */}
      <Card className="bg-slate-50 border-dashed">
        <CardContent className="pt-6">
          <div className="flex justify-between items-center">
             <span className="font-medium text-slate-600">Total Weight:</span>
             <span className="text-xl font-bold font-mono text-primary">
                {Object.values(weights).reduce((a, b) => a + b, 0).toFixed(2)}
             </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
