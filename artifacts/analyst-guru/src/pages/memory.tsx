import { useState } from "react";
import { useSearchMemory, useStoreMemory } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function Memory() {
  const [query, setQuery] = useState("");
  const searchMutation = useSearchMemory();
  const [results, setResults] = useState<any[]>([]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    try {
      const res = await searchMutation.mutateAsync({ data: { query } });
      setResults(res);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Memory Framework</h1>
        <p className="text-muted-foreground">Semantic knowledge graph across project scope.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Search Memory</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-6">
            <Input 
              placeholder="Search concepts, decisions, constraints..." 
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch} disabled={searchMutation.isPending || !query.trim()}>
              {searchMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Search className="h-4 w-4 mr-2" />}
              Search
            </Button>
          </div>

          <div className="space-y-4">
            {results.map((item) => (
              <div key={item.id} className="p-4 border rounded-md bg-card shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="secondary" className="uppercase text-[10px] tracking-wider">{item.memory_type}</Badge>
                  {item.project_name && <Badge variant="outline" className="text-[10px]">{item.project_name}</Badge>}
                  {item.relevance_score && <span className="text-xs text-muted-foreground ml-auto">Score: {item.relevance_score.toFixed(2)}</span>}
                </div>
                <p className="text-sm">{item.content}</p>
              </div>
            ))}
            {results.length === 0 && !searchMutation.isPending && query && (
              <div className="text-center py-8 text-muted-foreground border border-dashed rounded-md">
                No memories matched your search.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
