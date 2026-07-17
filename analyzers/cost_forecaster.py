from typing import Dict, Any

def forecast_deployment_costs(provider: str, estimated_traffic: int) -> Dict[str, Any]:
    """
    Estimates estimated monthly operational costs for a chosen cloud provider
    based on estimated monthly traffic.
    """
    provider_clean = provider.strip().lower()
    
    # Initialize response structure
    report = {
        "provider": provider,
        "estimated_traffic_monthly_requests": estimated_traffic,
        "base_cost": 0.0,
        "bandwidth_cost": 0.0,
        "database_cost": 0.0,
        "compute_cost": 0.0,
        "total_cost": 0.0,
        "free_tier_covered": False,
        "price_scaling_tier": "Free / Hobby",
        "detailed_metrics": {}
    }
    
    if provider_clean == "vercel":
        # Vercel Serverless
        # Hobby tier: 100 GB bandwidth, free
        # Pro tier: $20 base, 1 TB bandwidth included, then $40 per 100 GB. 
        # Serverless Function Execution: 100 GB-hours free, then $0.60 per million executions.
        million_requests = estimated_traffic / 1_000_000
        estimated_bandwidth_gb = estimated_traffic * 0.00015  # Avg 150KB per page/api response
        
        if estimated_traffic <= 100_000 and estimated_bandwidth_gb <= 100:
            report["free_tier_covered"] = True
            report["total_cost"] = 0.0
            report["price_scaling_tier"] = "Hobby Tier (Free)"
        else:
            report["price_scaling_tier"] = "Pro Tier"
            report["base_cost"] = 20.0
            
            # Bandwidth: 1TB free on Pro, then $40 per 100GB
            extra_bandwidth_gb = max(0.0, estimated_bandwidth_gb - 1000)
            report["bandwidth_cost"] = (extra_bandwidth_gb / 100.0) * 40.0
            
            # Compute: 1M requests included, then $0.60 per million
            extra_requests = max(0.0, million_requests - 1)
            report["compute_cost"] = extra_requests * 0.60
            report["total_cost"] = report["base_cost"] + report["bandwidth_cost"] + report["compute_cost"]
            
        report["detailed_metrics"] = {
            "estimated_bandwidth_gb": round(estimated_bandwidth_gb, 2),
            "serverless_executions_millions": round(million_requests, 2)
        }
        
    elif provider_clean == "supabase":
        # Supabase Hosting
        # Free Tier: 500MB DB storage, 2GB bandwidth, free
        # Pro Tier: $25/month base, includes 8GB DB, 250GB bandwidth, 100K active users (MAU)
        # Extra: $0.125/GB DB storage, $0.09/GB bandwidth, $0.00325/MAU
        db_storage_gb = 8.0 if estimated_traffic > 500_000 else 1.0
        mau = int(estimated_traffic * 0.1)  # MAU is approx 10% of total monthly traffic
        bandwidth_gb = estimated_traffic * 0.00005  # 50KB per request
        
        if mau <= 50_000 and bandwidth_gb <= 2 and db_storage_gb <= 0.5:
            report["free_tier_covered"] = True
            report["total_cost"] = 0.0
            report["price_scaling_tier"] = "Free Tier"
        else:
            report["price_scaling_tier"] = "Pro Tier"
            report["base_cost"] = 25.0
            
            # Bandwidth overage: Pro includes 250GB, then $0.09/GB
            extra_bandwidth = max(0.0, bandwidth_gb - 250)
            report["bandwidth_cost"] = extra_bandwidth * 0.09
            
            # DB Storage overage: Pro includes 8GB, then $0.125/GB
            extra_db = max(0.0, db_storage_gb - 8.0)
            report["database_cost"] = extra_db * 0.125
            
            # MAU overage: Pro includes 100k, then $0.00325 per MAU
            extra_mau = max(0, mau - 100_000)
            report["compute_cost"] = extra_mau * 0.00325
            
            report["total_cost"] = report["base_cost"] + report["bandwidth_cost"] + report["database_cost"] + report["compute_cost"]
            
        report["detailed_metrics"] = {
            "estimated_bandwidth_gb": round(bandwidth_gb, 2),
            "estimated_db_storage_gb": round(db_storage_gb, 2),
            "estimated_monthly_active_users": mau
        }
        
    elif provider_clean == "neon":
        # Neon Serverless Postgres
        # Free Tier: 0.5 GiB storage, 1 project, free
        # Launch Plan: $19/month base, includes 10 GiB storage, 300 Compute Hours
        # Scale Plan: $69/month base, includes 40 GiB storage, 750 Compute Hours
        compute_hours = estimated_traffic * 0.001  # Estimating 1 hour per 1000 requests due to auto-suspend
        db_storage_gb = 5.0 if estimated_traffic <= 100_000 else 25.0
        
        if db_storage_gb <= 0.5 and compute_hours <= 100:
            report["free_tier_covered"] = True
            report["total_cost"] = 0.0
            report["price_scaling_tier"] = "Free Tier"
        elif db_storage_gb <= 10.0 and compute_hours <= 300:
            report["price_scaling_tier"] = "Launch Plan"
            report["base_cost"] = 19.0
            report["total_cost"] = 19.0
        else:
            report["price_scaling_tier"] = "Scale Plan"
            report["base_cost"] = 69.0
            extra_db = max(0.0, db_storage_gb - 40.0)
            report["database_cost"] = extra_db * 0.12  # $0.12 per GB over 40GB
            extra_compute = max(0.0, compute_hours - 750)
            report["compute_cost"] = extra_compute * 0.10  # $0.10 per compute hour over 750
            report["total_cost"] = report["base_cost"] + report["database_cost"] + report["compute_cost"]
            
        report["detailed_metrics"] = {
            "estimated_db_storage_gb": db_storage_gb,
            "estimated_compute_hours": round(compute_hours, 1)
        }
        
    elif provider_clean == "aws":
        # AWS (Serverless Lambda + DynamoDB + API Gateway + CloudFront)
        # API Gateway: $3.50 per million API calls
        # Lambda: $0.20 per million requests + $0.0000166667 per GB-second (Assume 128MB, 200ms duration => 0.025 GB-sec/req)
        # CloudFront: $0.08 per GB egress
        # DynamoDB: $0.25 per GB storage + write/read capacity units (assume small load)
        million_requests = estimated_traffic / 1_000_000
        bandwidth_gb = estimated_traffic * 0.0001  # 100KB per response
        
        report["price_scaling_tier"] = "AWS Pay-as-you-go"
        report["base_cost"] = 0.0
        report["bandwidth_cost"] = bandwidth_gb * 0.08
        
        # API Gateway cost
        apigw_cost = million_requests * 3.50
        # Lambda cost
        lambda_exec_cost = million_requests * 0.20
        lambda_compute_cost = million_requests * 1_000_000 * 0.025 * 0.0000166667
        
        report["compute_cost"] = apigw_cost + lambda_exec_cost + lambda_compute_cost
        
        # DynamoDB cost
        db_storage_gb = 5.0 if estimated_traffic <= 100_000 else 50.0
        report["database_cost"] = db_storage_gb * 0.25
        
        # Deduct AWS Free Tier limits if traffic is very small (1M lambda requests, 1M API gateway calls, etc.)
        if estimated_traffic <= 1_000_000:
            # Free tier covers lambda & dynamo base storage
            report["database_cost"] = max(0.0, report["database_cost"] - 6.25)  # 25GB free
            report["compute_cost"] = max(0.0, report["compute_cost"] - 1.0)
            
        report["total_cost"] = report["base_cost"] + report["bandwidth_cost"] + report["database_cost"] + report["compute_cost"]
        report["detailed_metrics"] = {
            "api_gateway_cost": round(apigw_cost, 2),
            "lambda_cost": round(lambda_exec_cost + lambda_compute_cost, 2),
            "cloudfront_bandwidth_gb": round(bandwidth_gb, 2)
        }
        
    else:
        # Generic cloud provider backup
        report["price_scaling_tier"] = "Standard VM Hosting (Estimate)"
        report["base_cost"] = 15.0  # basic VPS cost
        bandwidth_gb = estimated_traffic * 0.0001
        report["bandwidth_cost"] = max(0.0, bandwidth_gb - 1000) * 0.01  # $0.01 per GB over 1TB
        report["total_cost"] = report["base_cost"] + report["bandwidth_cost"]
        
    # Standardize values
    report["base_cost"] = round(report["base_cost"], 2)
    report["bandwidth_cost"] = round(report["bandwidth_cost"], 2)
    report["database_cost"] = round(report["database_cost"], 2)
    report["compute_cost"] = round(report["compute_cost"], 2)
    report["total_cost"] = round(report["total_cost"], 2)
    
    return report
