"""
创建分层数据分区
解决历史数据可见性问题
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime, timedelta
import logging

# 添加ETL工具函数
sys.path.append(os.path.dirname(__file__))
from etl_utils import load_config

def create_layered_partitions():
    """
    创建分层数据分区：
    1. 热数据层：最近7天，日常使用
    2. 温数据层：最近30天，周报分析  
    3. 冷数据层：全部历史，月报/趋势分析
    """
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), "..", "03_配置文件", "config", "config_mes_batch_report.yaml")
    cfg = load_config(config_path)
    
    # 设置日志
    log_config = cfg.get("logging", {})
    log_file = log_config.get("file", "../06_日志文件/layered_partitions.log")
    log_file = os.path.join(os.path.dirname(__file__), log_file) if not os.path.isabs(log_file) else log_file
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_config.get("level", "INFO")),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # 读取处理后的数据
        output_dir = cfg.get("output", {}).get("base_dir", "")
        processed_file = os.path.join(output_dir, "MES_batch_report_latest.parquet")
        
        if not os.path.exists(processed_file):
            logger.error(f"处理后的数据文件不存在: {processed_file}")
            return
        
        df = pd.read_parquet(processed_file)
        logger.info(f"读取数据: {len(df)} 行")
        
        # 确保TrackOutDate是日期类型
        if 'TrackOutDate' in df.columns:
            df['TrackOutDate'] = pd.to_datetime(df['TrackOutDate']).dt.date
        
        # 创建分层目录
        base_partition_dir = os.path.join(output_dir, "layered_partitions")
        hot_dir = os.path.join(base_partition_dir, "hot")      # 热数据：最近7天
        warm_dir = os.path.join(base_partition_dir, "warm")    # 温数据：最近30天
        cold_dir = os.path.join(base_partition_dir, "cold")    # 冷数据：全部历史
        
        for dir_path in [hot_dir, warm_dir, cold_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        now = datetime.now().date()
        
        # 1. 热数据层：最近7天
        hot_cutoff = now - timedelta(days=7)
        hot_data = df[df['TrackOutDate'] >= hot_cutoff]
        
        # 按日期分区热数据
        hot_partitions = {}
        for date, group in hot_data.groupby('TrackOutDate'):
            date_str = date.strftime('%Y%m%d')
            partition_file = os.path.join(hot_dir, f"hot_{date_str}.parquet")
            
            group.to_parquet(partition_file, compression='snappy')
            hot_partitions[date_str] = {
                'file': f"hot/hot_{date_str}.parquet",
                'date': date_str,
                'rows': len(group),
                'layer': 'hot'
            }
        
        logger.info(f"热数据层创建完成: {len(hot_partitions)} 个分区，{len(hot_data)} 行")
        
        # 2. 温数据层：最近30天（排除热数据）
        warm_cutoff = now - timedelta(days=30)
        warm_data = df[(df['TrackOutDate'] >= warm_cutoff) & (df['TrackOutDate'] < hot_cutoff)]
        
        # 按周分区温数据
        warm_partitions = {}
        if not warm_data.empty:
            warm_data['Week'] = pd.to_datetime(warm_data['TrackOutDate']).dt.isocalendar().week
            warm_data['Year'] = pd.to_datetime(warm_data['TrackOutDate']).dt.year
            
            for (year, week), group in warm_data.groupby(['Year', 'Week']):
                partition_key = f"{year}_W{week:02d}"
                partition_file = os.path.join(warm_dir, f"warm_{partition_key}.parquet")
                
                group.to_parquet(partition_file, compression='snappy')
                warm_partitions[partition_key] = {
                    'file': f"warm/warm_{partition_key}.parquet",
                    'week': partition_key,
                    'rows': len(group),
                    'layer': 'warm'
                }
        
        logger.info(f"温数据层创建完成: {len(warm_partitions)} 个分区，{len(warm_data)} 行")
        
        # 3. 冷数据层：30天前的历史数据
        cold_data = df[df['TrackOutDate'] < warm_cutoff]
        
        # 按月分区冷数据
        cold_partitions = {}
        if not cold_data.empty:
            cold_data['Month'] = pd.to_datetime(cold_data['TrackOutDate']).dt.to_period('M')
            
            for month, group in cold_data.groupby('Month'):
                month_str = month.strftime('%Y%m')
                partition_file = os.path.join(cold_dir, f"cold_{month_str}.parquet")
                
                group.to_parquet(partition_file, compression='snappy')
                cold_partitions[month_str] = {
                    'file': f"cold/cold_{month_str}.parquet",
                    'month': month_str,
                    'rows': len(group),
                    'layer': 'cold'
                }
        
        logger.info(f"冷数据层创建完成: {len(cold_partitions)} 个分区，{len(cold_data)} 行")
        
        # 保存分层元数据
        metadata = {
            'created_at': datetime.now().isoformat(),
            'total_rows': len(df),
            'date_range': {
                'start': df['TrackOutDate'].min().isoformat(),
                'end': df['TrackOutDate'].max().isoformat()
            },
            'layers': {
                'hot': {
                    'description': '最近7天数据，日常快速刷新',
                    'partitions': hot_partitions,
                    'total_rows': len(hot_data),
                    'refresh_frequency': '每日'
                },
                'warm': {
                    'description': '最近30天数据，周报分析',
                    'partitions': warm_partitions,
                    'total_rows': len(warm_data),
                    'refresh_frequency': '每周'
                },
                'cold': {
                    'description': '历史数据，月报/趋势分析',
                    'partitions': cold_partitions,
                    'total_rows': len(cold_data),
                    'refresh_frequency': '每月'
                }
            }
        }
        
        metadata_file = os.path.join(base_partition_dir, "layered_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"分层元数据保存至: {metadata_file}")
        
        # 创建PowerBI分层查询模板
        create_layered_query_template(base_partition_dir, logger)
        
        logger.info("分层数据分区创建完成！")
        
    except Exception as e:
        logger.error(f"创建分层分区失败: {e}")
        raise

def create_layered_query_template(partition_dir, logger):
    """创建PowerBI分层查询模板"""
    
    query_template = """
// PowerBI分层数据查询模板
// 支持热、温、冷数据层智能切换

let
    // 参数设置（可在PowerBI中创建参数动态控制）
    Layer = "hot",        // "hot" | "warm" | "cold"
    PartitionPath = "{partition_path}",
    
    // 读取分层元数据
    GetLayerMetadata = (partitionPath as text, layerName as text) =>
        let
            JsonContent = Json.Document(File.Contents(partitionPath & "/layered_metadata.json")),
            layerData = JsonContent[layers][layerName],
            partitions = layerData[partitions],
            partitionList = Record.FieldValues(partitions)
        in
            {
                Partitions = partitionList,
                Description = layerData[description],
                TotalRows = layerData[total_rows]
            },
    
    // 获取指定层数据
    GetLayerData = (partitionPath as text, layerName as text) =>
        let
            layerInfo = GetLayerMetadata(partitionPath, layerName),
            partitionFiles = List.Transform(
                layerInfo[Partitions],
                each Parquet.Document(File.Contents(partitionPath & "/" & _[file]))
            ),
            combinedData = Table.Combine(partitionFiles)
        in
            combinedData,
    
    // 主数据源
    Source = GetLayerData(PartitionPath, Layer),
    
    // 类型转换
    #"Changed Type" = Table.TransformColumnTypes(Source, {{
        "TrackOutDate", type date},
        "TrackOutTime", type datetime},
        {"BatchNumber", type text},
        {"Operation", type text},
        {"CFN", type text},
        {"PT(d)", type number},
        {"ST(d)", type number},
        {"CompletionStatus", type text}
    }),
    
    // 添加数据层标记
    #"Added Layer" = Table.AddColumn(#"Changed Type", "DataLayer", each Layer, type text)
    
in
    #"Added Layer"
""".format(partition_path=partition_dir.replace('\\', '/'))
    
    # 保存查询模板
    query_file = os.path.join(partition_dir, "PowerBI_Layered_Query.m")
    with open(query_file, 'w', encoding='utf-8') as f:
        f.write(query_template)
    
    logger.info(f"PowerBI分层查询模板保存至: {query_file}")

if __name__ == "__main__":
    create_layered_partitions()
