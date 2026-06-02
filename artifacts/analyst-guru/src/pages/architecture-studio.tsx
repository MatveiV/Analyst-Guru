import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useListDocuments, getListDocumentsQueryKey } from "@workspace/api-client-react";
import { useLanguage } from "@/lib/i18n";

export default function ArchitectureStudio() {
  const { t } = useLanguage();

  const { data: _documents } = useListDocuments({ limit: 100 }, {
    query: { queryKey: getListDocumentsQueryKey({ limit: 100 }) }
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t.arch_title}</h1>
        <p className="text-muted-foreground">{t.arch_subtitle}</p>
      </div>

      <Tabs defaultValue="c4" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="c4">{t.arch_tab_c4}</TabsTrigger>
          <TabsTrigger value="uml">{t.arch_tab_uml}</TabsTrigger>
          <TabsTrigger value="erd">{t.arch_tab_erd}</TabsTrigger>
          <TabsTrigger value="api">{t.arch_tab_api}</TabsTrigger>
          <TabsTrigger value="adr">{t.arch_tab_adr}</TabsTrigger>
          <TabsTrigger value="architecture">{t.arch_tab_recs}</TabsTrigger>
        </TabsList>

        <TabsContent value="c4">
          <Card>
            <CardHeader>
              <CardTitle>{t.arch_c4_title}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-12 text-center text-muted-foreground border-2 border-dashed rounded-md">
                {t.arch_c4_hint}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="uml">
          <Card>
            <CardHeader><CardTitle>{t.arch_tab_uml}</CardTitle></CardHeader>
            <CardContent>
              <div className="p-12 text-center text-muted-foreground border-2 border-dashed rounded-md">
                {t.arch_c4_hint}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="erd">
          <Card>
            <CardHeader><CardTitle>{t.arch_tab_erd}</CardTitle></CardHeader>
            <CardContent>
              <div className="p-12 text-center text-muted-foreground border-2 border-dashed rounded-md">
                {t.arch_c4_hint}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api">
          <Card>
            <CardHeader><CardTitle>{t.arch_tab_api}</CardTitle></CardHeader>
            <CardContent>
              <div className="p-12 text-center text-muted-foreground border-2 border-dashed rounded-md">
                {t.arch_c4_hint}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="adr">
          <Card>
            <CardHeader><CardTitle>{t.arch_tab_adr}</CardTitle></CardHeader>
            <CardContent>
              <div className="p-12 text-center text-muted-foreground border-2 border-dashed rounded-md">
                {t.arch_c4_hint}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="architecture">
          <Card>
            <CardHeader><CardTitle>{t.arch_tab_recs}</CardTitle></CardHeader>
            <CardContent>
              <div className="p-12 text-center text-muted-foreground border-2 border-dashed rounded-md">
                {t.arch_c4_hint}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
