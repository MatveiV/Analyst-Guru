import { useGetDashboardStats, getGetDashboardStatsQueryKey, useGetRecentActivity, getGetRecentActivityQueryKey } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Files, SearchCheck, BrainCircuit, ShieldAlert, ArrowRight, Clock, Activity, Loader2, Cuboid } from "lucide-react";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useGetDashboardStats({
    query: {
      queryKey: getGetDashboardStatsQueryKey(),
    }
  });

  const { data: activity, isLoading: activityLoading } = useGetRecentActivity({ limit: 10 }, {
    query: {
      queryKey: getGetRecentActivityQueryKey({ limit: 10 }),
    }
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">System status and recent analyst activities.</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button asChild variant="outline" className="bg-white">
            <Link href="/documents/new">New Document</Link>
          </Button>
          <Button asChild>
            <Link href="/reviews">Start Review</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <Files className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /> : (
              <>
                <div className="text-2xl font-bold">{stats?.total_documents ?? 0}</div>
                <p className="text-xs text-muted-foreground mt-1">Managed in system</p>
              </>
            )}
          </CardContent>
        </Card>
        
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Reviews Performed</CardTitle>
            <SearchCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /> : (
              <>
                <div className="text-2xl font-bold">{stats?.total_reviews ?? 0}</div>
                <p className="text-xs text-muted-foreground mt-1">AI-assisted analyses</p>
              </>
            )}
          </CardContent>
        </Card>
        
        <Card className="shadow-sm border-l-4 border-l-destructive">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Needs Review</CardTitle>
            <ShieldAlert className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            {statsLoading ? <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /> : (
              <>
                <div className="text-2xl font-bold text-destructive">{stats?.needs_review_count ?? 0}</div>
                <p className="text-xs text-muted-foreground mt-1">Items requiring human check</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="shadow-sm border-l-4 border-l-primary">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Knowledge Base</CardTitle>
            <BrainCircuit className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            {statsLoading ? <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /> : (
              <>
                <div className="text-2xl font-bold">{stats?.total_kb_documents ?? 0}</div>
                <p className="text-xs text-muted-foreground mt-1">Indexed artifacts</p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-7">
        <Card className="md:col-span-5 shadow-sm">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest system operations and AI generations.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activityLoading ? (
                <div className="flex justify-center p-8">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : activity?.length === 0 ? (
                <div className="text-center p-8 text-muted-foreground border border-dashed rounded-md">
                  No recent activity found.
                </div>
              ) : (
                activity?.map((item) => (
                  <div key={item.id} className="flex items-start gap-4 border-b pb-4 last:border-0 last:pb-0">
                    <div className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${item.status === 'error' ? 'bg-destructive' : item.needs_review ? 'bg-yellow-500' : 'bg-primary'}`} />
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium leading-none">{item.action}</p>
                        <div className="flex items-center text-xs text-muted-foreground">
                          <Clock className="mr-1 h-3 w-3" />
                          {new Date(item.created_at).toLocaleString()}
                        </div>
                      </div>
                      {item.description && (
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {item.description}
                        </p>
                      )}
                      <div className="flex items-center gap-2 mt-2">
                        {item.needs_review && (
                          <span className="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">
                            ⚠️ Требует проверки
                          </span>
                        )}
                        <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">
                          {item.duration_ms ? `${(item.duration_ms / 1000).toFixed(1)}s` : '<1s'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2 shadow-sm bg-secondary/30">
          <CardHeader>
            <CardTitle>Quick Workflows</CardTitle>
            <CardDescription>Common operations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button asChild variant="outline" className="w-full justify-start bg-white">
              <Link href="/documents">
                <Files className="mr-2 h-4 w-4 text-muted-foreground" />
                Browse Documents
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full justify-start bg-white">
              <Link href="/reviews">
                <SearchCheck className="mr-2 h-4 w-4 text-muted-foreground" />
                Pending Reviews
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full justify-start bg-white">
              <Link href="/knowledge-base?tab=ask">
                <BrainCircuit className="mr-2 h-4 w-4 text-muted-foreground" />
                Ask Knowledge Base
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full justify-start bg-white">
              <Link href="/architecture-studio">
                <Cuboid className="mr-2 h-4 w-4 text-muted-foreground" />
                Design Architecture
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
