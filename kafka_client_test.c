/** @file */ 
#include <limits.h>
static struct fuse_context* test_fuse_get_context()
{
    static struct fuse_context ctx = { 0 };
    return &ctx;
}
typedef struct { } rd_kafka_t;
typedef struct { } rd_kafka_topic_t;
typedef struct { } rd_kafka_conf_t;
typedef struct { } rd_kafka_topic_conf_t;
typedef int rd_kafka_conf_res_t;
typedef int rd_kafka_type_t;
#define RD_KAFKA_CONF_OK 1
#define RD_KAFKA_PRODUCER 42
#define RD_KAFKA_PARTITION_UA 42
#define RD_KAFKA_MSG_F_COPY 42
rd_kafka_conf_t *rd_kafka_conf_new () { return 0; }
rd_kafka_topic_conf_t *rd_kafka_topic_conf_new () { return 0; }
void rd_kafka_conf_set_dr_cb (rd_kafka_conf_t *conf, void *f) { }
typedef struct
{
    int setup;
    rd_kafka_conf_res_t rd_kafka_conf_set_returns;
    char* rd_kafka_conf_set_fails_for;
    int rd_kafka_new_returns_NULL;
    int rd_kafka_topic_new_returns_NULL;
    int rd_kafka_brokers_add_returns;
    int rd_kafka_produce_returns;
    int asprintf_sets_NULL;
    int test_filler_returns;
} test_config;
static test_config* test_with()
{
    static test_config conf;
    if(!conf.setup)
    {
        conf.rd_kafka_brokers_add_returns = 1;
        conf.setup = 1;
    }
    return &conf;
}
#define asprintf(x, ...) (test_with()->asprintf_sets_NULL? (*x = NULL) == NULL : asprintf(x, __VA_ARGS__))
rd_kafka_conf_res_t rd_kafka_conf_set (rd_kafka_conf_t *conf,
				       const char *name,
				       const char *value,
				       char *errstr, size_t errstr_size)
{
    if(test_with()->rd_kafka_conf_set_fails_for == NULL)
            return test_with()->rd_kafka_conf_set_returns;
    else
        return strcmp(test_with()->rd_kafka_conf_set_fails_for,
                name) == 0?0:RD_KAFKA_CONF_OK;
}
rd_kafka_t *rd_kafka_new (rd_kafka_type_t type, rd_kafka_conf_t *conf,
			  char *errstr, size_t errstr_size)
{
    static rd_kafka_t rk;
    return test_with()->rd_kafka_new_returns_NULL ? NULL:&rk;
}
void rd_kafka_set_logger (rd_kafka_t *rk, void *f) { }
void rd_kafka_set_log_level (rd_kafka_t *rk, int level) { }
int rd_kafka_brokers_add (rd_kafka_t *rk, const char *brokerlist)
{ return test_with()->rd_kafka_brokers_add_returns; }
rd_kafka_topic_t *rd_kafka_topic_new (rd_kafka_t *rk, const char *topic,
				      rd_kafka_topic_conf_t *conf)
                                      {
                                          static rd_kafka_topic_t t;
                                          return test_with()->rd_kafka_topic_new_returns_NULL ? NULL:&t;
                                      }
const char *rd_kafka_topic_name (const rd_kafka_topic_t *rkt) { return 0; }
int rd_kafka_produce (rd_kafka_topic_t *rkt, int32_t partitition,
		      int msgflags,
		      void *payload, size_t len,
		      const void *key, size_t keylen,
		      void *msg_opaque)
{ return test_with()->rd_kafka_produce_returns; }

