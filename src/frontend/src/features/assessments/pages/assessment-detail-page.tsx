import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useAuthStore } from '@/features/auth/store/auth.store';
import { useAssessment } from '../api/assessments.api';
import { DomainNav } from '../components/domain-nav';
import { QuestionItem } from '../components/question-item';
import { DownloadReportButton } from '../components/download-report-button';
import { DelegationDialog } from '../components/delegation-dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useTranslation } from 'react-i18next';

export const AssessmentDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const { data: assessment, isLoading, error } = useAssessment(id!);
  const [activeDomainId, setActiveDomainId] = useState<string | null>(null);
  const { t } = useTranslation();

  useEffect(() => {
    if (assessment?.domains?.length && !activeDomainId) {
      setActiveDomainId(assessment.domains[0].id);
    }
  }, [assessment, activeDomainId]);

  if (isLoading) {
    return <div className="p-8 space-y-4">
      <Skeleton className="h-12 w-1/3" />
      <div className="flex gap-6">
        <Skeleton className="h-[400px] w-1/4" />
        <Skeleton className="h-[400px] w-3/4" />
      </div>
      <p className="text-sm text-muted-foreground animate-pulse">{t('common.loading')}</p>
    </div>;
  }

  if (error || !assessment) {
    return (
      <div className="container py-8">
        <Alert variant="destructive">
          <AlertTitle>{t('common.error')}</AlertTitle>
          <AlertDescription>{t('assessments.errorLoading') || 'Failed to load assessment details.'}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const isCompleted = assessment.status === 'COMPLETED';
  const activeDomain = assessment.domains?.find(d => d.id === activeDomainId);
  const user = useAuthStore(state => state.user);
  const canDelegate = user?.role === 'client_admin' || user?.role === 'super_admin';

  return (
    <div className="container py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{t('assessments.details')}</h1>
            <Badge variant="outline">{t(`assessments.status.${assessment.status}`)}</Badge>
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
             <span>{t('common.created')}: {new Date(assessment.createdAt).toLocaleDateString()}</span>
             {assessment.deadline && <span>{t('common.deadline')}: {new Date(assessment.deadline).toLocaleDateString()}</span>}
          </div>
        </div>
        <div className="flex gap-2">
           {isCompleted && (
              <DownloadReportButton assessmentId={assessment.id} />
           )}
           {!isCompleted && assessment.status !== 'ARCHIVED' && canDelegate && (
              <DelegationDialog 
                assessmentId={assessment.id} 
                organizationId={assessment.organizationId}
                domains={assessment.domains || []}
              />
           )}
        </div>
      </div>
      <Progress value={assessment.score || 0} className="w-full max-w-md h-2 mt-2" />
      <span className="text-sm font-medium">{t('common.overallScore')}: {assessment.score?.toFixed(1) || 0}%</span>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">{t('assessments.domains')}</CardTitle>
            </CardHeader>
            <CardContent className="p-2">
              <DomainNav 
                domains={assessment.domains || []}
                activeDomainId={activeDomainId}
                onSelectDomain={setActiveDomainId}
              />
            </CardContent>
          </Card>
        </div>

        {/* content */}
        <div className="lg:col-span-3">
          {activeDomain ? (
            <div className="space-y-6">
              <div className="border-b pb-4 mb-4">
                 <h2 className="text-xl font-semibold">{t('assessments.domainNames.' + activeDomain.domainId)}</h2>
                 <p className="text-muted-foreground">
                   {t('assessments.domainDescription')}
                 </p>
                 <div className="mt-2 flex items-center gap-2">
                   <span className="text-sm font-medium">{t('assessments.score')}: {activeDomain.score?.toFixed(1) || 0}%</span>
                   <Badge variant="secondary">{t(`assessments.status.${activeDomain.status}`)}</Badge>
                   {activeDomain.assigneeId && <span className="text-xs text-muted-foreground">{t('assessments.assignedTo')}: {activeDomain.assigneeId}</span>}
                 </div>
              </div>

              {activeDomain.elements?.map((response) => (
                <QuestionItem 
                  key={response.id}
                  elementId={response.elementId}
                  domainId={activeDomain.id}
                  response={response}
                  readOnly={assessment.status === 'COMPLETED' || assessment.status === 'ARCHIVED'}
                />
              ))}
            </div>
          ) : (
             <div className="text-center py-10 text-muted-foreground">{t('assessments.selectDomain')}</div>
          )}
        </div>
      </div>
    </div>
  );
};
