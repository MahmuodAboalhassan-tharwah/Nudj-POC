import { Bell } from "lucide-react";
import { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { useNotifications, useUnreadCount, useMarkAsRead, useMarkAllAsRead } from "@/features/notifications/api/notifications.api";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

export function NotificationCenter() {
  const [open, setOpen] = useState(false);
  const { data: notifications, isLoading } = useNotifications();
  const { data: unreadCount = 0 } = useUnreadCount();
  const markAsRead = useMarkAsRead();
  const markAllAsRead = useMarkAllAsRead();

  const handleMarkAsRead = (id: string, isRead: boolean) => {
    if (!isRead) {
      markAsRead.mutate(id);
    }
  };

  const handleMarkAllRead = () => {
      markAllAsRead.mutate();
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative transition-transform active:scale-95">
          <Bell className="h-5 w-5 text-muted-foreground" />
          {unreadCount > 0 && (
            <span className="absolute top-2 right-2 h-2.5 w-2.5 rounded-full bg-primary ring-2 ring-background animate-pulse" />
          )}
          <span className="sr-only">Notifications</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0 shadow-2xl border-slate-200/60" align="end">
        <div className="flex items-center justify-between border-b bg-slate-50/50 px-4 py-3">
          <h4 className="text-sm font-bold tracking-tight">Notifications</h4>
          {unreadCount > 0 && (
            <Button 
                variant="ghost" 
                size="sm" 
                className="text-[10px] font-bold uppercase tracking-wider text-primary h-auto p-1.5 hover:bg-primary/10 rounded"
                onClick={handleMarkAllRead}
            >
              Mark all as read
            </Button>
          )}
        </div>
        <ScrollArea className="h-[400px]">
          {isLoading ? (
             <div className="p-8 text-center text-sm text-muted-foreground">
               <div className="h-5 w-48 bg-slate-100 animate-pulse rounded mx-auto mb-2" />
               <div className="h-4 w-32 bg-slate-50 animate-pulse rounded mx-auto" />
             </div>
          ) : !notifications || notifications.length === 0 ? (
            <div className="p-12 text-center">
              <div className="mx-auto w-12 h-12 rounded-full bg-slate-50 flex items-center justify-center mb-4">
                <Bell className="h-6 w-6 text-slate-300" />
              </div>
              <p className="text-sm font-medium text-slate-900">No notifications</p>
              <p className="text-xs text-slate-500 mt-1">We'll notify you when something happens.</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={cn(
                    "group flex flex-col gap-1 p-4 text-sm transition-all duration-200 hover:bg-slate-50/80 cursor-pointer relative",
                    !notification.is_read && "bg-primary/5"
                  )}
                  onClick={() => handleMarkAsRead(notification.id, notification.is_read)}
                >
                  {!notification.is_read && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                  )}
                  <div className="flex items-start justify-between gap-3">
                    <p className={cn("font-semibold leading-tight", !notification.is_read ? "text-slate-900" : "text-slate-600")}>
                      {notification.title}
                    </p>
                    <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-tighter whitespace-nowrap bg-slate-100 px-1.5 py-0.5 rounded">
                      {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-2 mt-0.5 font-medium leading-relaxed">
                    {notification.message}
                  </p>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
