import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLanguage } from "@/lib/i18n";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const API_BASE = import.meta.env.BASE_URL?.replace(/\/$/, "") || "";

const PROVIDERS = [
  { value: "anthropic", label: "Anthropic (Claude)" },
  { value: "openai", label: "OpenAI (GPT)" },
  { value: "proxyapi", label: "ProxyAPI" },
] as const;

export default function Settings() {
  const { t } = useLanguage();
  const [provider, setProvider] = useState("anthropic");
  const [apiKey, setApiKey] = useState("");
  const [hasApiKey, setHasApiKey] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/settings/ai`)
      .then((r) => r.json())
      .then((data) => {
        setProvider(data.provider);
        setHasApiKey(data.has_api_key);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE}/api/settings/ai`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider,
          api_key: apiKey || undefined,
        }),
      });
      if (!res.ok) throw new Error("Failed to save");
      const data = await res.json();
      setProvider(data.provider);
      setHasApiKey(data.has_api_key);
      setApiKey("");
      setMessage({ type: "success", text: t.settings_saved });
    } catch {
      setMessage({ type: "error", text: t.settings_error });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">{t.settings_title}</h1>
        <p className="text-muted-foreground mt-1">{t.settings_subtitle}</p>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>{t.settings_ai_title}</CardTitle>
          <CardDescription>{t.settings_ai_desc}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>{t.settings_provider}</Label>
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger className="w-full max-w-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PROVIDERS.map((p) => (
                  <SelectItem key={p.value} value={p.value}>
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>{t.settings_api_key}</Label>
            <Input
              type="password"
              placeholder={hasApiKey ? t.settings_key_placeholder_set : t.settings_key_placeholder_empty}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="max-w-sm"
            />
            {hasApiKey && provider && (
              <p className="text-xs text-muted-foreground">{t.settings_key_current}</p>
            )}
          </div>

          {message && (
            <div className={`flex items-center gap-2 text-sm ${message.type === "success" ? "text-green-600" : "text-destructive"}`}>
              {message.type === "success" ? <CheckCircle2 className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
              {message.text}
            </div>
          )}

          <Button onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            {t.settings_save_btn}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
