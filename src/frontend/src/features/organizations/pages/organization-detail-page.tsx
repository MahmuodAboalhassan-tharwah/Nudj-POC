import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { OrganizationForm } from '../components/organization-form';
import { useOrganization, useCreateOrganization, useUpdateOrganization } from '../api/organizations.api';
import { OrganizationCreatePayload } from '../types/organization.types';
import { toast } from 'sonner';

export const OrganizationDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = id === 'new';

  const { data: organization, isLoading: isLoadingOrg } = useOrganization(id as string);
  const createMutation = useCreateOrganization();
  const updateMutation = useUpdateOrganization();

  const handleSubmit = async (data: OrganizationCreatePayload) => {
    try {
      if (isNew) {
        await createMutation.mutateAsync(data);
        toast.success("Organization created successfully");
        navigate('/admin/organizations');
      } else if (id) {
        await updateMutation.mutateAsync({ id, data });
        toast.success("Organization updated successfully");
      }
    } catch (error) {
      toast.error("Failed to save organization");
    }
  };

  if (!isNew && isLoadingOrg) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" onClick={() => navigate('/admin/organizations')}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back
        </Button>
        <h1 className="text-3xl font-bold tracking-tight">
          {isNew ? 'Create Organization' : 'Edit Organization'}
        </h1>
      </div>
      
      <div className="bg-card border rounded-lg p-6">
        <OrganizationForm 
          initialData={organization} 
          onSubmit={handleSubmit}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      </div>
    </div>
  );
};
