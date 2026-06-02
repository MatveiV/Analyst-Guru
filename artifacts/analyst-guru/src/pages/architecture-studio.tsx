import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useListDocuments, getListDocumentsQueryKey } from "@workspace/api-client-react";
import { Loader2 } from "lucide-react";

export default function ArchitectureStudio() {
  const { data: documents, isLoading } = useListDocuments({ limit: 100 }, {
    query: {
      queryKey: getListDocumentsQueryKey({ limit: 100 }),
    }
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Architecture Studio</h1>
        <p className="text-muted-foreground">Design system architectures, APIs, and ADRs.</p>
      </div>

      <Tabs defaultValue="c4" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="c4">C4 Diagrams</TabsTrigger>
          <TabsTrigger value="uml">UML</TabsTrigger>
          <TabsTrigger value="erd">ERD</TabsTrigger>
          <TabsTrigger value="api">API Design</TabsTrigger>
          <TabsTrigger value="adr">ADRs</TabsTrigger>
          <TabsTrigger value="architecture">Recommendations</TabsTrigger>
        </TabsList>
        
        <TabsContent value="c4">
          <Card>
            <CardHeader>
              <CardTitle>Generate C4 Diagrams</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-12 text-center text-muted-foreground border-2 border-dashed rounded-md">
                Select a document to generate Context, Container, and Component diagrams.
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        {/* Additional tabs omitted for brevity but would follow same pattern */}
      </Tabs>
    </div>
  );
}
