-- Projects Table
CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Components Table
CREATE TABLE IF NOT EXISTS components (
    component_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    properties JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Assets Table
CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    folder TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    metadata JSON,
    project_id INTEGER,
    preview_image TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Templates Table
CREATE TABLE IF NOT EXISTS templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    category TEXT,
    properties JSON,
    preview_image TEXT,
    description TEXT,
    layout_data TEXT, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_default BOOLEAN DEFAULT 0
);

-- User Templates Table
CREATE TABLE IF NOT EXISTS user_templates (
    user_template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    project_id INTEGER,
    name TEXT NOT NULL,
    modified_properties JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(template_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Settings Table
CREATE TABLE IF NOT EXISTS settings (
    settings_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER UNIQUE,
    theme JSON,
    default_sizes JSON,
    export_preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- App Settings Table
CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY,
    settings JSON NOT NULL
);

-- Asset Tags Table (for organizing assets)
CREATE TABLE IF NOT EXISTS asset_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    tag_name TEXT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

-- Component Assets Table (for linking components with assets)
CREATE TABLE IF NOT EXISTS component_assets (
    component_id INTEGER,
    asset_id INTEGER,
    position_x INTEGER,
    position_y INTEGER,
    width INTEGER,
    height INTEGER,
    layer_order INTEGER,
    PRIMARY KEY (component_id, asset_id),
    FOREIGN KEY (component_id) REFERENCES components(component_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

-- Asset Folders Table
CREATE TABLE IF NOT EXISTS asset_folders (
    folder_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    project_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES asset_folders(folder_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Add folder_id column to assets table
-- ALTER TABLE assets ADD COLUMN folder_id INTEGER REFERENCES asset_folders(folder_id); 