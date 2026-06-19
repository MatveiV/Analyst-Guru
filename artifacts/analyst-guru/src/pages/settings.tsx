import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
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

const PROVIDER_CONFIGS: Record<string, {
  label: string;
  models: { value: string; label: string }[];
  defaultBaseUrl: string;
  supportsBaseUrl: boolean;
}> = {
  openrouter: {
    label: "OpenRouter",
    defaultBaseUrl: "https://openrouter.ai/api/v1",
    supportsBaseUrl: true,
    models: [
      { value: "openrouter/free", label: "openrouter/free" },
      { value: "openrouter/auto", label: "openrouter/auto" },
      { value: "anthropic/claude-3.5-sonnet", label: "Claude 3.5 Sonnet" },
      { value: "openai/gpt-4o", label: "GPT-4o" },
      { value: "google/gemini-2.0-flash", label: "Gemini 2.0 Flash" },
      { value: "meta-llama/llama-3.3-70b", label: "Llama 3.3 70B" },
      { value: "deepseek/deepseek-r1", label: "DeepSeek R1" },
      { value: "microsoft/phi-4", label: "Phi-4" },
      { value: "qwen/qwen2.5-vl-72b", label: "Qwen 2.5 VL 72B" },
    ],
  },
  anthropic: {
    label: "Anthropic (Claude)",
    defaultBaseUrl: "",
    supportsBaseUrl: false,
    models: [
      { value: "claude-3-5-sonnet-20241022", label: "Claude 3.5 Sonnet" },
      { value: "claude-3-opus-20240229", label: "Claude 3 Opus" },
      { value: "claude-3-haiku-20240307", label: "Claude 3 Haiku" },
      { value: "claude-3-5-haiku-20241022", label: "Claude 3.5 Haiku" },
    ],
  },
  openai: {
    label: "OpenAI (GPT)",
    defaultBaseUrl: "",
    supportsBaseUrl: true,
    models: [
      { value: "gpt-4o", label: "GPT-4o" },
      { value: "gpt-4o-mini", label: "GPT-4o Mini" },
      { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
      { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
    ],
  },
  proxyapi: {
    label: "ProxyAPI",
    defaultBaseUrl: "https://api.proxyapi.ru/openai/v1",
    supportsBaseUrl: true,
    models: [
      { value: "gpt-4o-mini", label: "GPT-4o Mini" },
      { value: "gpt-4o", label: "GPT-4o" },
      { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
    ],
  },
};

export default function Settings() {
  const { t } = useLanguage();
  const [provider, setProvider] = useState("openrouter");
  const [apiKey, setApiKey] = useState("");
  const [hasApiKey, setHasApiKey] = useState(false);
  const [baseUrl, setBaseUrl] = useState("");
  const [model, setModel] = useState("");
  const [temperature, setTemperature] = useState(0.2);
  const [maxTokens, setMaxTokens] = useState(4096);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const cfg = PROVIDER_CONFIGS[provider];

  useEffect(() => {
    fetch(`${API_BASE}/api/settings/ai`)
      .then((r) => r.json())
      .then((data) => {
        setProvider(data.provider);
        setHasApiKey(data.has_api_key);
        setBaseUrl(data.base_url || "");
        setModel(data.model || "");
        setTemperature(data.temperature ?? 0.2);
        setMaxTokens(data.max_tokens ?? 4096);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const body: Record<string, unknown> = { provider };
      if (apiKey) body.api_key = apiKey;
      if (baseUrl) body.base_url = baseUrl;
      if (model) body.model = model;
      body.temperature = temperature;
      body.max_tokens = maxTokens;

      const res = await fetch(`${API_BASE}/api/settings/ai`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const errBody = await res.text();
        throw new Error(errBody || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setProvider(data.provider);
      setHasApiKey(data.has_api_key);
      setBaseUrl(data.base_url || "");
      setModel(data.model || "");
      setTemperature(data.temperature ?? 0.2);
      setMaxTokens(data.max_tokens ?? 4096);
      setApiKey("");
      setMessage({ type: "success", text: t.settings_saved });
    } catch (e) {
      const detail = e instanceof Error ? e.message : "Unknown error";
      setMessage({ type: "error", text: `${t.settings_error}: ${detail}` });
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
            <Select value={provider} onValueChange={(v) => {
              const next = PROVIDER_CONFIGS[v];
              setProvider(v);
              setBaseUrl(next.defaultBaseUrl);
              setModel(next.models[0]?.value || "");
            }}>
              <SelectTrigger className="w-full max-w-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(PROVIDER_CONFIGS).map(([key, c]) => (
                  <SelectItem key={key} value={key}>
                    {c.label}
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

          {cfg.supportsBaseUrl && (
            <div className="space-y-2">
              <Label>{t.settings_base_url}</Label>
              <Input
                type="text"
                placeholder={t.settings_base_url_placeholder}
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                className="max-w-sm"
              />
            </div>
          )}

          <div className="space-y-2">
            <Label>{t.settings_model}</Label>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger className="w-full max-w-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {cfg.models.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2 max-w-sm">
            <Label>{t.settings_temperature}: {temperature.toFixed(1)}</Label>
            <Slider
              min={0}
              max={2}
              step={0.1}
              value={[temperature]}
              onValueChange={([v]) => setTemperature(v)}
            />
          </div>

          <div className="space-y-2">
            <Label>{t.settings_max_tokens}</Label>
            <Input
              type="number"
              min={256}
              max={131072}
              step={256}
              value={maxTokens}
              onChange={(e) => setMaxTokens(Number(e.target.value))}
              className="max-w-[180px]"
            />
          </div>

          {message && (
            <div className={`flex items-center gap-2 text-sm ${message.type === "success" ? "text-green-600" : "text-destructive"}`}>
              {message.type === "success" ? <CheckCircle2 className="h-4 w-4 shrink-0" /> : <AlertCircle className="h-4 w-4 shrink-0" />}
              <span className="break-all">{message.text}</span>
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
