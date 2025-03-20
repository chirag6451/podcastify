import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import {
  Mic,
  Settings,
  Bell,
  User,
  Home,
  Youtube,
  FileEdit,
  CreditCard,
  LogOut,
} from "lucide-react";

function Sidebar() {
  const [location, setLocation] = useLocation();

  const isActive = (path: string) => {
    return location.startsWith(path);
  };

  const handleLogout = () => {
    // TODO: Implement logout logic
    setLocation("/");
  };

  return (
    <div className="w-64 h-screen bg-sidebar border-r border-border flex flex-col fixed">
      <div className="p-4">
        <Link href="/dashboard">
          <a className="text-xl font-bold text-primary">Podcast Studio</a>
        </Link>
      </div>
      <nav className="flex-1 px-2 py-4 space-y-1">
        <Button 
          variant={isActive("/dashboard") ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => setLocation("/dashboard")}
        >
          <Home className="mr-2 h-4 w-4" />
          Dashboard
        </Button>
        <Button 
          variant={isActive("/podcasts") ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => setLocation("/podcasts")}
        >
          <Mic className="mr-2 h-4 w-4" />
          My Podcasts
        </Button>
        <Button 
          variant={isActive("/youtube") ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => setLocation("/youtube")}
        >
          <Youtube className="mr-2 h-4 w-4" />
          YouTube Management
        </Button>
        <Button 
          variant={isActive("/drafts") ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => setLocation("/drafts")}
        >
          <FileEdit className="mr-2 h-4 w-4" />
          Drafts
        </Button>
        <Button 
          variant={isActive("/notifications") ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => setLocation("/notifications")}
        >
          <Bell className="mr-2 h-4 w-4" />
          Notifications
        </Button>
        <Button 
          variant={isActive("/settings") ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => setLocation("/settings")}
        >
          <Settings className="mr-2 h-4 w-4" />
          Settings
        </Button>

        {/* Profile section */}
        <div className="pt-4 mt-4 border-t">
          <Button 
            variant={isActive("/profile") ? "secondary" : "ghost"}
            className="w-full justify-start"
            onClick={() => setLocation("/profile")}
          >
            <User className="mr-2 h-4 w-4" />
            Profile
          </Button>
          <Button 
            variant="ghost"
            className="w-full justify-start"
            onClick={() => setLocation("/profile?tab=subscription")}
          >
            <CreditCard className="mr-2 h-4 w-4" />
            Subscription
          </Button>
          <Button 
            variant="ghost"
            className="w-full justify-start text-red-500 hover:text-red-600"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </nav>
    </div>
  );
}

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 min-h-screen">
        {children}
      </main>
    </div>
  );
}