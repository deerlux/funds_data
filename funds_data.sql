/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2014/3/11 22:38:43                           */
/*==============================================================*/


drop table if exists fund_value;

drop table if exists funds_list;

drop table if exists funds_stock_data;

drop table if exists funds_type;

drop table if exists stock_list;

/*==============================================================*/
/* Table: fund_value                                            */
/*==============================================================*/
create table fund_value
(
   value_data_id        numeric(8,0) not null,
   fund_code            varchar(6) not null comment '基金代码',
   value_date           date not null,
   value_leiji          float comment '累积净值',
   value_curr           float comment '当日净值',
   primary key (value_data_id)
);

alter table fund_value comment '基金净值信息';

/*==============================================================*/
/* Table: funds_list                                            */
/*==============================================================*/
create table funds_list
(
   fund_code            varchar(6) not null comment '基金代码',
   type_id              int not null,
   fund_name            varchar(32) not null comment '基金名称',
   fund_origin_date     date,
   comment              varchar(256),
   primary key (fund_code)
);

alter table funds_list comment '基金列表';

/*==============================================================*/
/* Table: funds_stock_data                                      */
/*==============================================================*/
create table funds_stock_data
(
   fund_code            varchar(6) not null comment '基金代码',
   stock_code           varchar(8) not null,
   public_date          date comment '发布日期',
   primary key (fund_code, stock_code)
);

/*==============================================================*/
/* Table: funds_type                                            */
/*==============================================================*/
create table funds_type
(
   type_id              int not null,
   type_name            varchar(16) not null,
   primary key (type_id)
);

alter table funds_type comment '基金类型代码';

/*==============================================================*/
/* Table: stock_list                                            */
/*==============================================================*/
create table stock_list
(
   stock_code           varchar(8) not null,
   stock_name           varchar(32),
   primary key (stock_code)
);

alter table stock_list comment '股票列表';

alter table fund_value add constraint FK_Relationship_2 foreign key (fund_code)
      references funds_list (fund_code) on delete restrict on update restrict;

alter table funds_list add constraint FK_Relationship_1 foreign key (type_id)
      references funds_type (type_id) on delete restrict on update restrict;

alter table funds_stock_data add constraint FK_funds_stock_data foreign key (fund_code)
      references funds_list (fund_code) on delete restrict on update restrict;

alter table funds_stock_data add constraint FK_funds_stock_data2 foreign key (stock_code)
      references stock_list (stock_code) on delete restrict on update restrict;

