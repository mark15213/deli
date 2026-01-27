export type SourceType = 'X_SOCIAL' | 'NOTION_KB' | 'ARXIV_PAPER' | 'GITHUB_REPO' | 'WEB_RSS';

// --- Connection Configs ---

export interface XConnectionConfig {
    target_username: string;
    auth_mode: 'API_KEY' | 'OAUTH_USER';
    api_token: string;
}

export interface NotionConnectionConfig {
    workspace_id: string;
    integration_token: string;
    target_database_id?: string;
}

export interface ArxivConnectionConfig {
    base_url: string;
    category_filter: string[];
}

export interface GithubConnectionConfig {
    repo_url: string;
    branch: string;
    access_token?: string;
}

export interface RssConnectionConfig {
    url: string;
    type: 'RSS' | 'SITEMAP' | 'SINGLE_PAGE';
}

export type ConnectionConfig =
    | XConnectionConfig
    | NotionConnectionConfig
    | ArxivConnectionConfig
    | GithubConnectionConfig
    | RssConnectionConfig;

// --- Ingestion Rules ---

export interface XIngestionRules {
    scope: 'USER_FEED' | 'BOOKMARKS' | 'SEARCH_KEYWORD';
    include_replies: boolean;
    min_likes_threshold: number;
    fetch_frequency: 'HOURLY' | 'DAILY' | 'WEEKLY';
    grouping_strategy: 'THREAD' | 'SINGLE';
    ai_instruction?: string;
}

export interface NotionIngestionRules {
    sync_mode: 'INCREMENTAL' | 'FULL';
    property_map: Record<string, string>;
    import_nested_pages: boolean;
    ignore_status: string[];
    generate_flashcards: boolean;
}

export interface ArxivIngestionRules {
    search_query: string;
    parsing_depth: 'FULL_TEXT' | 'ABSTRACT_ONLY';
    translate_to?: string;
    math_handling: 'LATEX' | 'OCR';
    output_format: {
        summary_length: 'SHORT' | 'MEDIUM' | 'LONG';
        key_takeaways_count: number;
    };
}

export interface GithubIngestionRules {
    file_extensions: string[];
    ignore_paths: string[];
    max_file_size_kb: number;
    focus_on: 'ARCHITECTURE' | 'CODE_DETAILS';
    readme_priority: 'HIGHEST' | 'NORMAL';
}

export interface RssIngestionRules {
    content_selector?: string;
    exclude_keywords: string[];
    clean_mode: 'READABILITY' | 'RAW';
    auto_tagging: boolean;
}

export type IngestionRules =
    | XIngestionRules
    | NotionIngestionRules
    | ArxivIngestionRules
    | GithubIngestionRules
    | RssIngestionRules;

// --- Source Entity ---

export interface Source {
    id: string;
    user_id: string;
    name: string;
    type: SourceType;
    connection_config: ConnectionConfig;
    ingestion_rules: IngestionRules;
    status: 'ACTIVE' | 'PAUSED' | 'ERROR';
    last_synced_at?: string;
    error_log?: string;
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

export interface SuggestedConfig {
    fetch_mode?: string;
    recurrence?: string;
    tags?: string[];
    // Add other dynamic suggestions as needed
}

export interface FormSchema {
    allow_frequency_setting: boolean;
    allow_depth_setting: boolean;
    default_tags: string[];
}

export interface DetectResponse {
    status: string;
    detected_type: SourceType;
    metadata: PreviewMetadata;
    suggested_config: SuggestedConfig;
    form_schema?: FormSchema;
}
