CREATE TABLE widget (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL,
    label VARCHAR(255) NOT NULL CHECK (label <> ''),
    created_by VARCHAR(128) NOT NULL,
    updated_by VARCHAR(128) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX uniq_widget_label_per_tenant ON widget (tenant_id, label);
CREATE INDEX idx_widget_tenant_created_at ON widget (tenant_id, created_at DESC);
