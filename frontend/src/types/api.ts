export type UserType = {
    id: number;
    name: string;
    current_job_id: string;
    current_job_name: string;
    level: string;
};

export type ExpType = {
    current: string;
    next: string;
    percent: string;
};

export type JobType = {
    id: string;
    name: string | null;
};

export type StatusType = {
    id: string;
    name: string;
    value: number;
    type: string;
};

export type AchievementType = {
    achievement_name: string;
    title_name: string;
};

export type CategoryType = {
    id: string;
    name: string;
};

export type TodayLogType = {
    category_id: string;
    category_name: string;
    start_time: string;
    end_time: string;
    duration_seconds: string;
};

export type MasterCategoriesType = {
    id:string;
    name:string;
    is_active:boolean;
};

export type HomeDataType = {
    success: boolean;
    user: UserType;
    exp: ExpType;
    user_jobs: JobType[];
    user_statuses: StatusType[];
    user_achievements: AchievementType[];
    user_categories: CategoryType[];
    today_logs: TodayLogType[];
    is_admin: boolean;
};

export type categorySummaryType = {
    category_id: string;
    category_name: string;
    category_total_seconds: number;
};

export type dailyCategorySummaryType = {
    category_id:string;
    category_name:string;
    log_date: string;
    daily_total_seconds: number;
};



export type savedataType = {
    category_id: string;
    start_time: string | null;
    end_time: string;
    duration_seconds: number;
};

export type CategoryDataType = {
    user_categories: CategoryType[];
    master_categories: CategoryType[];
};

export type StatusDataType = {
    user:UserType;
    exp:ExpType;
    job:JobType[];
    status:StatusType[];
    achievements:AchievementType[];
};

export type HistoryDataType = {
    categorySummary:categorySummaryType[];
    dailyCategorySummary:dailyCategorySummaryType[];
};

export type PeriodType =
    | "all"
    | "today"
    | "7days"
    | "week"
    | "month"
    | "year";

export type UnitType = 
    | "seconds"
    | "minutes"
    | "hours";

export type MasterCategoriesDataType={
    MasterCategories:MasterCategoriesType[];
}

export type StatusTypeType=
    | "front"
    | "back"

export type StatusesType ={
    id:string;
    name:string;
    type:StatusTypeType;
    default_value:string;
    isActive:boolean;
}


export type StatusesDataType = {
    masterStatuses:StatusesType[]
}

export type AchievementsType = {
    id:string;
    category_id:string;
    category_name:string;
    required_hours:number;
    achievement_name:string;
    title_name:string;
    is_active:boolean;
}

export type AchievementsDataType = {
    achievements:AchievementsType[];
    mastercategories:MasterCategoriesType[];
}

export type StatusRulesType = {
    id:string;
    category_id:string;
    category_name:string;
    status_id:string;
    status_name:string;
    gain_per_hours:number;
    is_active:boolean;
}

export type StatusRulesDataType = {
    masterCategories:MasterCategoriesType[]
    masterStatuses:StatusesType[]
    statusRules:StatusRulesType[]
}

export type JobRequirementInputType = {
    statusId:string;
    requiredValue:string;
}

export type JobRequirementType = {
    id:string;
    jobId:string;
    statusId:string;
    statusName:string;
    requiredValue:string;
    isActive:boolean;
}

export type JobsType = {
    id:string;
    jobName:string;
    isActive:boolean;
    isDefault:boolean;
}

export type JobsDataType = {
    masterJobs:JobsType[]
    jobRequirements:JobRequirementType[]
    masterStatuses:StatusesType[]

}

export type AdminUserType = {
    id:string;
    username:string;
    userLevel:string;
    userCurrentJob:string | null;
    isAdmin:boolean;
    isActive:boolean;
}

export type AdminUsersDataType = {
    users:AdminUserType[];
}

