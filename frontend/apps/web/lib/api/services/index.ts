export { type PaginatedResponse } from "./qms";

export {
    type Document,
    type DocumentVersion,
    type DocumentDistribution,
    type QualityEvent,
    type QualityEventSummary,
    type CAPA,
    type CAPAAction,
    type Course,
    type TrainingAssignment,
    type Equipment,
    documentsApi, qualityEventsApi, capaApi, trainingApi, equipmentApi,
} from "./qms";

export {
    type Plate, type EMImage, type AIRun, type Job, type QAReview,
    platesApi, imagesApi, aiRunsApi, jobsApi, qaReviewsApi,
} from "./em";

export {
    type Customer, type Contract, type WorkOrder, type Technician, type Invoice, type Certificate,
    customersApi, contractsApi, workOrdersApi, techniciansApi, invoicesApi, certificatesApi,
} from "./ccv";

export {
    type User, type AuditEntry,
    usersApi, auditApi,
} from "./platform";

export {
    type PlatformKPIs, type DashboardMeta, type DashboardData, type TimeSeriesData,
    analyticsApi,
} from "./analytics";
