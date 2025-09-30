import type { TablePaginationConfig } from 'antd';
import type { FilterValue, SortOrder } from 'antd/es/table/interface';

// Interface designed to save the state of the filters, sorters and pagination when changing pages
interface FilterState {
    pagination: TablePaginationConfig;
    filters: Record<string, FilterValue | null>;
    sorters: Record<string, SortOrder | null>;
}

interface FilterContext {

}