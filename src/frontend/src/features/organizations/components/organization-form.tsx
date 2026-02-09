import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Organization, OrganizationCreatePayload } from '../types/organization.types';

const orgSchema = z.object({
  name_ar: z.string().min(2, 'Arabic name is required'),
  name_en: z.string().min(2, 'English name is required'),
  cr_number: z.string().optional(),
  sector: z.string().optional(),
  size: z.string().optional(),
  region: z.string().optional(),
  is_active: z.boolean().default(true),
});

type OrganizationFormValues = z.infer<typeof orgSchema>;

interface OrganizationFormProps {
  initialData?: Organization;
  onSubmit: (data: OrganizationCreatePayload) => void;
  isLoading?: boolean;
}

export const OrganizationForm = ({ initialData, onSubmit, isLoading }: OrganizationFormProps) => {
  const form = useForm<OrganizationFormValues>({
    resolver: zodResolver(orgSchema),
    defaultValues: initialData || {
      name_ar: '',
      name_en: '',
      cr_number: '',
      sector: '',
      size: '',
      region: '',
      is_active: true,
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="name_en"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Organization Name (English)</FormLabel>
                <FormControl>
                  <Input placeholder="Acme Corp" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="name_ar"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Organization Name (Arabic)</FormLabel>
                <FormControl>
                  <Input placeholder="شركة القمة" className="text-right" dir="rtl" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="cr_number"
            render={({ field }) => (
              <FormItem>
                <FormLabel>CR Number</FormLabel>
                <FormControl>
                  <Input placeholder="1010xxxxxx" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="sector"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Sector</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a sector" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="Technology">Technology</SelectItem>
                    <SelectItem value="Finance">Finance</SelectItem>
                    <SelectItem value="Healthcare">Healthcare</SelectItem>
                    <SelectItem value="Retail">Retail</SelectItem>
                    <SelectItem value="Energy">Energy</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="size"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Size</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select size" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="Micro (1-9)">Micro (1-9)</SelectItem>
                    <SelectItem value="Small (10-49)">Small (10-49)</SelectItem>
                    <SelectItem value="Medium (50-249)">Medium (50-249)</SelectItem>
                    <SelectItem value="Large (250+)">Large (250+)</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="region"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Region</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select region" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="Riyadh">Riyadh</SelectItem>
                    <SelectItem value="Makkah">Makkah</SelectItem>
                    <SelectItem value="Eastern Province">Eastern Province</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="is_active"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                <div className="space-y-0.5">
                  <FormLabel className="text-base">Active Status</FormLabel>
                </div>
                <FormControl>
                  <Switch
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        <div className="flex justify-end space-x-4">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Saving..." : "Save Organization"}
          </Button>
        </div>
      </form>
    </Form>
  );
};
