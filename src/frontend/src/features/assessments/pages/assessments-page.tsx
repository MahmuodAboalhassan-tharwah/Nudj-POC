import { AssessmentList } from '../components/assessment-list';
import { CreateAssessmentDialog } from '../components/create-assessment-dialog';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { useAuth } from '@/features/auth/hooks/use-auth';
import { Role } from '@/features/auth/types/auth.types';

export const AssessmentsPage = () => {
  const { hasRole } = useAuth();
  const canCreate = hasRole([Role.CLIENT_ADMIN, Role.SUPER_ADMIN, Role.ANALYST]);

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Assessments</h1>
          <p className="text-muted-foreground">Manage your organization's maturity assessments.</p>
        </div>
        {canCreate && (
          <CreateAssessmentDialog>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Assessment
            </Button>
          </CreateAssessmentDialog>
        )}
      </div>

      <AssessmentList />
    </div>
  );
};
