import { useNavigate } from 'react-router-dom';
import { Plus, Building2, MapPin, Users, Briefcase } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useOrganizations } from '../api/organizations.api';

export const OrganizationList = () => {
  const navigate = useNavigate();
  const { data: organizations, isLoading } = useOrganizations();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-48 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Organizations</h2>
        <Button onClick={() => navigate('new')}>
          <Plus className="mr-2 h-4 w-4" /> New Organization
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {organizations?.map((org) => (
          <Card 
            key={org.id} 
            className="cursor-pointer hover:bg-accent/50 transition-colors"
            onClick={() => navigate(org.id)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {org.name_en}
                <div className="text-xs text-muted-foreground mt-1">{org.name_ar}</div>
              </CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm mt-3">
                <div className="flex items-center text-muted-foreground">
                  <Briefcase className="mr-2 h-3 w-3" />
                  {org.sector || 'N/A'}
                </div>
                <div className="flex items-center text-muted-foreground">
                    <Users className="mr-2 h-3 w-3" />
                    {org.size || 'N/A'}
                </div>
                <div className="flex items-center text-muted-foreground">
                  <MapPin className="mr-2 h-3 w-3" />
                  {org.region || 'N/A'}
                </div>
              </div>
              <div className="mt-4 flex items-center justify-between">
                  <Badge variant={org.is_active ? "default" : "secondary"}>
                      {org.is_active ? "Active" : "Inactive"}
                  </Badge>
                  {org.cr_number && (
                      <span className="text-xs text-muted-foreground">CR: {org.cr_number}</span>
                  )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
