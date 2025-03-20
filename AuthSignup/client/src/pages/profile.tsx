import { useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  CreditCard,
  LogOut,
  User,
  Clock,
  CreditCardIcon,
  Download,
  History,
  BarChart3,
  Wallet
} from "lucide-react";

export default function Profile() {
  const [, setLocation] = useLocation();

  const handleLogout = () => {
    // TODO: Implement logout logic
    setLocation("/");
  };

  // Get the active tab from URL parameters
  const searchParams = new URLSearchParams(window.location.search);
  const activeTab = searchParams.get('tab') || 'profile';

  // Mock data for credit usage
  const creditData = {
    available: 50,
    totalMinutes: 40,
    episodesCreated: 5,
    creditsUsedThisMonth: 40,
    percentageRemaining: 55
  };

  const creditHistory = [
    { date: 'Mar 2, 2025', title: 'AI in Business', minutes: 15, credits: 15 },
    { date: 'Mar 5, 2025', title: 'Marketing Trends', minutes: 10, credits: 10 },
    { date: 'Mar 10, 2025', title: 'Fitness Talk', minutes: 5, credits: 5 }
  ];

  const creditPackages = [
    { credits: 10, minutes: 10, price: 5 },
    { credits: 50, minutes: 50, price: 20 },
    { credits: 100, minutes: 100, price: 35 },
    { credits: 500, minutes: 500, price: 150 }
  ];

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold mb-8">Profile</h1>

        {activeTab === 'profile' && (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Profile Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Full Name</Label>
                  <Input placeholder="Enter your name" />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input type="email" placeholder="Enter your email" />
                </div>
                <div className="space-y-2">
                  <Label>Profile Picture</Label>
                  <Input type="file" accept="image/*" />
                </div>
                <Button>Save Changes</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Change Password</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Current Password</Label>
                  <Input type="password" placeholder="Enter current password" />
                </div>
                <div className="space-y-2">
                  <Label>New Password</Label>
                  <Input type="password" placeholder="Enter new password" />
                </div>
                <div className="space-y-2">
                  <Label>Confirm New Password</Label>
                  <Input type="password" placeholder="Confirm new password" />
                </div>
                <Button>Update Password</Button>
              </CardContent>
            </Card>
          </>
        )}

        {activeTab === 'subscription' && (
          <>
            {/* Current Credits Balance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wallet className="w-5 h-5" />
                  Current Credits Balance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-2xl font-bold">
                  {creditData.available} credits remaining
                  <span className="text-sm text-muted-foreground ml-2">
                    (~{creditData.available} minutes of podcasting)
                  </span>
                </div>
                <Progress value={creditData.percentageRemaining} className="h-2" />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div className="p-4 bg-muted rounded-lg">
                    <div className="text-sm text-muted-foreground">Episodes Created</div>
                    <div className="text-2xl font-semibold">{creditData.episodesCreated}</div>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <div className="text-sm text-muted-foreground">Minutes Used</div>
                    <div className="text-2xl font-semibold">{creditData.totalMinutes} mins</div>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <div className="text-sm text-muted-foreground">Credits Used This Month</div>
                    <div className="text-2xl font-semibold">{creditData.creditsUsedThisMonth}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Buy Credits */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCardIcon className="w-5 h-5" />
                  Buy More Credits
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {creditPackages.map((pkg, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <div className="font-semibold">{pkg.credits} Credits</div>
                        <div className="text-sm text-muted-foreground">
                          {pkg.minutes} Minutes of podcasting
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-xl font-bold">${pkg.price}</div>
                        <Button>Buy Now</Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Credit Usage History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <History className="w-5 h-5" />
                  Credit Usage History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border">
                  <div className="grid grid-cols-4 gap-4 p-4 border-b bg-muted">
                    <div className="font-semibold">Date</div>
                    <div className="font-semibold">Podcast Title</div>
                    <div className="font-semibold text-right">Minutes Used</div>
                    <div className="font-semibold text-right">Credits Used</div>
                  </div>
                  {creditHistory.map((item, index) => (
                    <div key={index} className="grid grid-cols-4 gap-4 p-4 border-b last:border-0">
                      <div>{item.date}</div>
                      <div>{item.title}</div>
                      <div className="text-right">{item.minutes} min</div>
                      <div className="text-right">{item.credits} credits</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Payment Methods */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="w-5 h-5" />
                  Payment Methods
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <CreditCard className="w-6 h-6" />
                    <div>
                      <div className="font-semibold">Visa ending in 4242</div>
                      <div className="text-sm text-muted-foreground">Expires 12/25</div>
                    </div>
                  </div>
                  <Button variant="outline">Edit</Button>
                </div>
                <Button className="w-full">
                  Add New Payment Method
                </Button>
              </CardContent>
            </Card>
          </>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Account Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              variant="destructive"
              className="w-full flex items-center gap-2"
              onClick={handleLogout}
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}