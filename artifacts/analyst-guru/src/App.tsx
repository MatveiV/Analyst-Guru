import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Layout } from "@/components/layout";
import Dashboard from "@/pages/dashboard";
import Documents from "@/pages/documents";
import DocumentDetail from "@/pages/document-detail";
import Reviews from "@/pages/reviews";
import ReviewDetail from "@/pages/review-detail";
import KnowledgeBase from "@/pages/knowledge-base";
import ArchitectureStudio from "@/pages/architecture-studio";
import Memory from "@/pages/memory";
import Audit from "@/pages/audit";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/documents" component={Documents} />
        <Route path="/documents/:id" component={DocumentDetail} />
        <Route path="/reviews" component={Reviews} />
        <Route path="/reviews/:id" component={ReviewDetail} />
        <Route path="/knowledge-base" component={KnowledgeBase} />
        <Route path="/architecture-studio" component={ArchitectureStudio} />
        <Route path="/memory" component={Memory} />
        <Route path="/audit" component={Audit} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
