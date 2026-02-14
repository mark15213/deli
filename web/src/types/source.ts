// --- Source Types ---

export type SourceCategory = 'SNAPSHOT' | 'SUBSCRIPTION';

export type SourceType =
    // Snapshot Types (one-time parse)
    | 'ARXIV_PAPER'
    | 'WEB_ARTICLE'
    | 'TWEET_THREAD'
    | 'GITHUB_REPO'
    | 'MANUAL_NOTE'
    | 'PDF_DOCUMENT'
    // Subscription Types (periodic sync)
    | 'RSS_FEED'
    | 'HF_DAILY_PAPERS'
    | 'AUTHOR_BLOG'
    // Legacy (backwards compatibility)
    | 'X_SOCIAL'
    | 'NOTION_KB'
    | 'WEB_RSS';

// Subscription types set
export const SUBSCRIPTION_TYPES = new Set<SourceType>([
    'RSS_FEED',
    'HF_DAILY_PAPERS',
    'AUTHOR_BLOG',
]);

export function isSubscriptionType(type: SourceType): boolean {
    return SUBSCRIPTION_TYPES.has(type);
}

// --- Connection Configs ---

export interface ArxivConnectionConfig {
    url: string;
    arxiv_id?: string;
}

export interface WebArticleConnectionConfig {
    url: string;
}

export interface GithubConnectionConfig {
    repo_url: string;
    branch: string;
    access_token?: string;
}

export interface RssConnectionConfig {
    url: string;
}

export interface TweetConnectionConfig {
    url: string;
    tweet_id?: string;
}

export interface XConnectionConfig {
    target_username: string;
    api_token: string;
}

export interface XIngestionRules {
    scope: 'USER_FEED' | 'BOOKMARKS' | 'SEARCH_KEYWORD';
    include_replies: boolean;
    min_likes_threshold: number;
    grouping_strategy: 'THREAD' | 'SINGLE';
}

export type ConnectionConfig =
    | ArxivConnectionConfig
    | WebArticleConnectionConfig
    | GithubConnectionConfig
    | RssConnectionConfig
    | TweetConnectionConfig
    | XConnectionConfig
    | Record<string, any>;

// --- Subscription Configs ---

export type SyncFrequency = 'HOURLY' | 'DAILY' | 'WEEKLY';

export interface BaseSubscriptionConfig {
    sync_frequency: SyncFrequency;
    enabled: boolean;
    sync_hour?: number;  // 0-23, default 20 (8 PM)
    last_cursor?: string;
    last_synced_at?: string;
}

export interface RSSSubscriptionConfig extends BaseSubscriptionConfig {
    max_items_per_sync: number;
    title_include_keywords: string[];
    title_exclude_keywords: string[];
    content_min_length: number;
}

export interface HFDailyPapersConfig extends BaseSubscriptionConfig {
    categories: string[];
    min_upvotes: number;
    include_abstracts: boolean;
    max_papers_per_sync: number;
}

export interface AuthorBlogConfig extends BaseSubscriptionConfig {
    content_selector?: string;
    link_selector?: string;
    date_selector?: string;
    max_pages_to_crawl: number;
    url_pattern?: string;
}

export type SubscriptionConfig =
    | RSSSubscriptionConfig
    | HFDailyPapersConfig
    | AuthorBlogConfig
    | Record<string, any>;

// --- Source Material ---

export interface SourceMaterial {
    id: string;
    title?: string;
    external_url?: string;
    created_at?: string;
    rich_data: {
        summary?: string;
        suggestions?: Array<{
            key: string;
            name: string;
            description: string;
            reason: string;
        }>;
        lenses?: Record<string, any>;
        [key: string]: any;
    };
}

// --- Source Entity ---

import { User } from './user';
// ... (Source interface definition)
export interface Source {
    id: string;
    user_id?: string;
    user?: User;
    name: string;
    type: SourceType;
    category: SourceCategory;
    connection_config: ConnectionConfig;
    ingestion_rules: Record<string, any>;
    subscription_config?: SubscriptionConfig;
    status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'ACTIVE' | 'PAUSED' | 'FAILED';
    last_synced_at?: string;
    next_sync_at?: string;
    error_log?: string;
    parent_source_id?: string;
    children_count?: number;
    source_materials?: SourceMaterial[];
    created_at?: string;
}

// --- Source Create ---

export interface SourceCreate {
    name: string;
    type: SourceType;
    connection_config: Record<string, any>;
    ingestion_rules?: Record<string, any>;
    subscription_config?: SubscriptionConfig;
}

// --- Detection Types ---

export interface DetectRequest {
    input: string;
    check_connectivity?: boolean;
}

export interface PreviewMetadata {
    title: string;
    description?: string;
    icon_url?: string;
    author?: string;
    url?: string;
    image?: string;
}

export interface SubscriptionPreviewItem {
    title: string;
    url: string;
    date?: string;
}

export interface SubscriptionHints {
    suggested_frequency: SyncFrequency;
    estimated_items_per_day?: number;
    preview_items: SubscriptionPreviewItem[];
    form_schema?: Record<string, any>;  // JSON Schema for config form
}

export interface FormSchema {
    allow_frequency_setting: boolean;
    allow_depth_setting?: boolean;
    default_tags: string[];
}

export interface DetectResponse {
    status: string;
    detected_type: SourceType;
    category: SourceCategory;
    metadata: PreviewMetadata;
    suggested_config: Record<string, any>;
    form_schema?: FormSchema;
    subscription_hints?: SubscriptionHints;
}

// --- Form Field Types (for dynamic subscription config forms) ---

export interface SubscriptionFormField {
    key: string;
    label: string;
    type: 'text' | 'number' | 'select' | 'multiselect' | 'toggle' | 'textarea';
    required: boolean;
    default?: any;
    options?: Array<{ value: string; label: string }>;
    description?: string;
    min?: number;
    max?: number;
}

export interface SubscriptionFormSchema {
    source_type: string;
    fields: SubscriptionFormField[];
}
