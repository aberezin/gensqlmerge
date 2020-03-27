#! /usr/bin/env python
from __future__ import print_function
import pytds,getpass,os,re,functools,operator
import click
import sys
#The Merge Statement for sqlserver is not concurrancy safe out of the box.
#see https://michaeljswart.com/2017/07/sql-server-upsert-patterns-and-antipatterns/
# and
#The merge statement that this generator creates will not be safe.  You need to add your own lock hints etc.

# Run this for completion script: _GENERATE_MERGE_COMPLETE=source ./generate_merge > complete.sh
@click.command()
@click.option("--user", default="aberezin", help="not yet used")
@click.option("--src-database-name", default="transTTL", help="not yet used")
@click.option("--dest-database-name", default="transtitle", help="not yet used")
@click.option("--server", default="transttl-replica-1.acertuslabs.com", help="not yet used")
@click.option("--source-sql", default="select 1",
              help="The sql that selects the source table.  Defaults to \"select 1\" so you can tweek later.")
@click.option("--dest-table", default="tblDest", help="Fully qualified table name.")
@click.option("--on-condition", help="The match on condition. Use 'src' and 'dest' for table aliases.")
@click.option("--compare-columns", \
              help="The column names for the columns that are updated: Format is:\
               destColumnName:srcColumnName[:<options>] [,...N] where <options> ::= castdate")
@click.option("--compare-columns-file", \
              help="A file with one row per pair of columns. Lines that have a '#' in them are ignored.  Each row is formatted like:\
               destColumnName:srcColumnName [:<options>] where <options> ::= castdate")
@click.option("--insert-columns",default="id:newid() ,othercode:1",\
              help="These columns are only inserted, not updated. The insert-columns will usually include the columns used \
               for the on-condition.  Format is: destColumnName:srcStatement [,...N]")
def main(user,src_database_name,dest_database_name,server, source_sql, dest_table,on_condition, compare_columns,\
          compare_columns_file,insert_columns):
    if (compare_columns_file and compare_columns):
        eprint("you cannot set both compare-columns and compare-columns-file")
        exit(1);

    if (on_condition is None):
        eprint("You must specify an --on-condition .  See --help")
        exit(1)

    dest_database_schema = "dbo"
    # envkey=src_database_name+'_pw'
    # try:
    #     pw = os.environ[envkey]
    # except:
    #     pw =  getpass.getpass('pw (nothing in '+envkey+'): ')

    sql = f"MERGE {dest_database_name}.{dest_database_schema}.{dest_table} as dest\n"
    sql += f"USING ({source_sql}) as src\n"
    sql += f"ON {on_condition}\n"
    sql += f"WHEN MATCHED AND (1 = 0 \n"
    sql += f"--BE CAREFUL comparing dates!  Safer to cast(mycol as Date) and compare that. \n"

    ccolumns = getCompareColumns(compare_columns, compare_columns_file)
    for ccol in ccolumns:
        dest_col,src_col = dest_src_split(ccol)
        # TODO when the source is not nullable as when you call isNull(someCol,'foo') then we dont need all this.
        # Also, when dest is not nullable we dont need those tests
        sql += f"or (dest.{dest_col} is null and src.{src_col} is not null) " \
        + f"or (dest.{dest_col} is not null and src.{src_col} is null)" \
        + f"or dest.{dest_col} <> src.{src_col}\n "
    sql += ") THEN UPDATE\n" \
        + "SET\n"

    def build_assignment(ccol):
        dest_col,src_col = dest_src_split(ccol)
        return f" {dest_col} = src.{src_col} "

    sql += "\n,".join(map(build_assignment,ccolumns )) \
        + "\nWHEN NOT MATCHED THEN\n"\
        + "INSERT ("
    icolumns = [ icol for icol in re.split(r"\s*,\s*",insert_columns) ]
    icolumns_dest = map(lambda x: dest_src_split(x)[0]  ,icolumns)
    icolumns_src = map(lambda x: dest_src_split(x)[1]  ,icolumns)
    ccolumns_dest = map(lambda x: dest_src_split(x)[0]  ,ccolumns)
    ccolumns_src = map(lambda x: "src."+dest_src_split(x)[1]  ,ccolumns)
    sql += "\n,".join(icolumns_dest) +"\n," \
        + "\n,".join(ccolumns_dest) \
        + ")\n VALUES (" \
        + "\n,".join(icolumns_src) +"\n," \
        + "\n,".join(ccolumns_src) \
        + ");"

    print(sql)

    # conn = pytds.connect(dsn=server,
    #                      user=user,
    #                      password=pw,
    #                      database=src_database_name)
    # sql = """
    #     """
    # conn.close()


def getCompareColumns(compare_columns, compare_columns_file):
    if (compare_columns_file):
        with open(compare_columns_file) as f:
            return [x.strip() for x in f.readlines() if x.strip() != "" and not re.match("^\s*#.*", x)]
    else:
        return [icol for icol in re.split(r"\s*,\s*", compare_columns)]


def dest_src_split(str):
    return tuple([x.strip() for x in str.split(":")])

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':
    main()

