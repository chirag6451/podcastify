import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FaGoogle } from "react-icons/fa";
import { ExternalLink } from "lucide-react";

export default function Auth() {
  const [, setLocation] = useLocation();

  const handleContinue = () => {
    setLocation("/register");
  };

  // Temporary function for direct dashboard access
  const handleTempDashboard = () => {
    setLocation("/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="absolute inset-0 bg-cover bg-center opacity-10 -z-10" 
           style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1590069261209-f8e9b8642343")' }} />

      <Card className="w-full max-w-md mx-4 shadow-xl relative z-10">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
            Podcast Studio
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center text-gray-600 mb-6">
            Create and manage your podcasts with AI
          </div>
          <Button
            onClick={handleContinue}
            className="w-full py-6 text-lg flex items-center justify-center gap-3 hover:bg-primary/90 transition-colors"
            type="button"
          >
            <FaGoogle className="w-5 h-5" />
            Continue with Google
          </Button>

          {/* Visit Website Button */}
          <Button
            variant="outline"
            className="w-full py-6 text-lg flex items-center justify-center gap-3"
            onClick={() => window.open(window.location.origin + '/website', '_blank')}
          >
            <ExternalLink className="w-5 h-5" />
            Visit Our Website
          </Button>

          {/* Temporary button for direct dashboard access */}
          <div className="pt-4 border-t">
            <Button
              onClick={handleTempDashboard}
              variant="secondary"
              className="w-full"
              type="button"
            >
              Temporary: Go to Dashboard
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}