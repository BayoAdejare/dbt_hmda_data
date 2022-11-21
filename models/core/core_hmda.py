from snowflake.snowpark.functions import lit


def model(dbt, session):
    dbt.config(materialized="table")

    df_hmda = dbt.ref("base_hmda")

    # Calculate overall approval rate
    df_approval_rates = calculate_overall_approval(df_hmda)

    return df_approval_rates


def calculate_overall_approval(df):
    """
    Calculates the overall approval rate based on action_taken. 
    Approvals:
        1.Loan originated
        2.Application approved but not accepted 
    Denials:
        3.Application denied by financial institution
    Other action_taken codes removed.
    """
    # filters for relevant applications
    df_filter_approvals = (df["action_taken"] >= 1) & (df["action_taken"] <= 2)
    df_filter_approvals_denials = (df["action_taken"] >= 1) & (df["action_taken"] <= 3)

    # approved applications
    df_filtered_approvals = df.where(df_filter_approvals)

    # other application status remove
    df_filtered_approvals_denials = df.where(df_filter_approvals_denials)

    # overall approval rate
    approval_rates = (
        df_filtered_approvals.count() / df_filtered_approvals_denials.count()
    )

    df_approval_rates = df_filtered_approvals_denials.with_column(
        "overall_approval_rates", lit(approval_rates)
    )
    return df_approval_rates
