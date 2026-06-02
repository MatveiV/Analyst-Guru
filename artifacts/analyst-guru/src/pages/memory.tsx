import { useState } from "react";
import { useSearchMemory } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/lib/i18n";

export default function Memory() {
  const { t } = useLanguage();
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
        <h1 className="text-3xl font-bold tracking-tight">{t.memory_title}</h1>
        <p className="text-muted-foreground">{t.memory_subtitle}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t.memory_search_title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-6">
            <Input
              data-testid="input-memory-search"
              placeholder={t.memory_search_placeholder}
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
            />
            <Button
              onClick={handleSearch}
              disabled={searchMutation.isPending || !query.trim()}
              data-testid="button-memory-search"
            >
              {searchMutation.isPending
                ? <Loader2 className="h-4 w-4 animate-spin mr-2" />
                : <Search className="h-4 w-4 mr-2" />}
              {t.memory_search_btn}
            </Button>
          </div>

          <div className="space-y-4">
            {results.map((item) => (
              <div key={item.id} className="p-4 border rounded-md bg-card shadow-sm" data-testid={`card-memory-${item.id}`}>
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="secondary" className="uppercase text-[10px] tracking-wider">{item.memory_type}</Badge>
                  {item.project_name && <Badge variant="outline" className="text-[10px]">{item.project_name}</Badge>}
                  {item.relevance_score && (
                    <span className="text-xs text-muted-foreground ml-auto">{t.memory_score} {item.relevance_score.toFixed(2)}</span>
                  )}
                </div>
                <p className="text-sm">{item.content}</p>
              </div>
            ))}
            {results.length === 0 && !searchMutation.isPending && query && (
              <div className="text-center py-8 text-muted-foreground border border-dashed rounded-md">
                {t.memory_empty}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
