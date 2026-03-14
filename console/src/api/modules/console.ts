import { request } from "../request";

export interface PushMessage {
  id: string;
  text: string;
}

export interface ConsolePluginManifest {
  path: string;
  label: string;
  icon: string;
  entry: string;
}

export const consoleApi = {
  getPushMessages: () =>
    request<{ messages: PushMessage[] }>("/console/push-messages"),

  /** Plugins that add console tabs/pages (built-in + installed marketplace). */
  getPlugins: () =>
    request<ConsolePluginManifest[]>("/console/plugins"),
};
