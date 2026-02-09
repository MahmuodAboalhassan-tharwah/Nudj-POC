import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { useAssessments } from '../api/assessments.api';
import { AssessmentStatus } from '../types/assessment.types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useTranslation } from 'react-i18next';

export const AssessmentList = () => {
  const { t } = useTranslation();
  const { data: assessments, isLoading, error } = useAssessments();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-[200px] w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500">{t('assessments.list.failed')}</div>;
  }

  if (!assessments?.length) {
    return (
      <div className="text-center py-10">
        <p className="text-muted-foreground">{t('assessments.list.noAssessments')}</p>
        <Button variant="link" onClick={() => {}}>{t('assessments.list.createOne')}</Button>
      </div>
    );
  }

  const getStatusColor = (status: AssessmentStatus) => {
    switch (status) {
      case AssessmentStatus.COMPLETED: return 'bg-green-500';
      case AssessmentStatus.IN_PROGRESS: return 'bg-blue-500';
      case AssessmentStatus.DRAFT: return 'bg-gray-400';
      default: return 'bg-slate-500';
    }
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {assessments.map((assessment) => (
        <Card key={assessment.id} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => navigate(`/assessments/${assessment.id}`)}>
          <CardHeader>
            <div className="flex justify-between items-start">
              <CardTitle>{t('assessments.list.title')}</CardTitle>
              <Badge className={getStatusColor(assessment.status)}>
                {t(`assessments.status.${assessment.status.toLowerCase()}`)}
              </Badge>
            </div>
            <CardDescription>{t('assessments.list.created')} {format(new Date(assessment.createdAt), 'PP')}</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm font-medium">{t('assessments.list.score')}: {assessment.score ? `${assessment.score.toFixed(1)}%` : 'N/A'}</p>
            {assessment.deadline && (
              <p className="text-sm text-muted-foreground mt-2">{t('assessments.list.deadline')}: {format(new Date(assessment.deadline), 'PP')}</p>
            )}
          </CardContent>
          <CardFooter>
            <Button variant="outline" className="w-full">{t('assessments.list.viewDetails')}</Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};
