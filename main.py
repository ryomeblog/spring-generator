import json
import psycopg2
import re
import os
import logging


def makeDir(path):
    os.makedirs(path, exist_ok=True)


def openFile(path, filename):
    filePath = path + '/' + filename
    f = open(filePath, 'r', encoding="utf-8")
    data = f.read()
    f.close()
    return data


def makeFile(path, filename, text):
    filePath = path + '/' + filename
    f = open(filePath, 'w', encoding="utf-8")
    f.write(text)
    f.close()


def snakeToUpperCamel(str):
    res = re.sub("_(.)", lambda x: x.group(1).upper(), str)
    return res[0].upper() + res[1:]


def snakeToCamel(str):
    return re.sub("_(.)", lambda x: x.group(1).upper(), str)


def camelToSnake(str):
    return re.sub("([A-Z])", lambda x: "_" + x.group(1).lower(), str)


def camelToPath(str):
    return re.sub("([A-Z])", lambda x: "/" + x.group(1).lower(), str)


def snakeToUpperSnake(str):
    return re.sub("([a-z])", lambda x: x.group(1).upper(), str)


def typeConversion(str):
    convType = "none"
    if str == 'character varying':
        convType = 'String'
    if str == 'character':
        convType = 'String'
    if str == 'text':
        convType = 'String'
    if str == 'integer':
        convType = 'Integer'
    if str == 'smallint':
        convType = 'Short'
    if str == 'bigint':
        convType = 'Long'
    if str == 'numeric':
        convType = 'Short'
    if str == 'real':
        convType = 'Float'
    if str == 'double precision':
        convType = 'Double'
    if str == 'date':
        convType = 'Date'
    if str == 'timestamp without time zone':
        convType = 'Date'
    if str == 'bytea':
        convType = 'byte[]'
    if str == 'boolean':
        convType = 'Boolean'
    return convType


def dataTypeConversion(str):
    convType = str
    if str == 'character varying':
        convType = 'VARCHAR'
    if str == 'boolean':
        convType = 'BIT'
    return snakeToUpperSnake(convType)


def parsetype(type, str):
    parseStr = str
    if type == 'Integer':
        parseStr = 'toInt(' + str + ')'
    if type == 'Short':
        parseStr = 'toShort(' + str + ')'
    if type == 'Long':
        parseStr = 'toLong(' + str + ')'
    if type == 'Float':
        parseStr = 'toFloat(' + str + ')'
    if type == 'Double':
        parseStr = 'toDouble(' + str + ')'
    if type == 'Date':
        parseStr = 'toDate(' + str + ')'
    if type == 'byte[]':
        parseStr = 'toByte(' + str + ')'
    if type == 'Boolean':
        parseStr = 'toBoolean(' + str + ')'
    return parseStr


def get_db(settings):
    logging.debug('=====PostgreSQL Connect start=====')
    connector = psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
        user=settings['db']['user'],  # ユーザ
        password=settings['db']['password'],  # パスワード
        host=settings['db']['host'],  # ホスト名
        port=settings['db']['port'],  # ポート
        dbname=settings['db']['dbname']))  # データベース名

    logging.debug('Get tablename')
    cur = connector.cursor()
    cur.execute("SELECT tablename from pg_tables where schemaname='public';")

    logging.debug('Json Conversion')
    results = cur.fetchall()
    res = []
    for result in results:
        cur.execute(
            "select column_name, data_type, character_maximum_length from information_schema.columns "
            "where table_name='" + result[0] + "' order by ordinal_position;")
        dataTypeList = cur.fetchall()
        columns = []
        for dataType in dataTypeList:
            dataTypeJson = {}
            dataTypeJson['column_name'] = snakeToCamel(dataType[0])
            dataTypeJson['upper_column_name'] = snakeToUpperCamel(dataType[0])
            dataTypeJson['data_type'] = dataType[1]
            dataTypeJson['conv_type'] = typeConversion(dataType[1])
            dataTypeJson['character_maximum_length'] = dataType[2]
            columns.append(dataTypeJson)
        cur.execute(
            "SELECT DISTINCT ccu.column_name as pk_name, cs.data_type as pk_type "
            "FROM information_schema.table_constraints tc "
            "INNER JOIN information_schema.constraint_column_usage ccu "
            "ON ( "
            "tc.table_catalog = ccu.table_catalog "
            "and tc.table_schema = ccu.table_schema "
            "and tc.table_name = ccu.table_name "
            "and tc.constraint_name = ccu.constraint_name)  "
            "INNER JOIN information_schema.columns cs "
            "ON cs.column_name = ccu.column_name "
            "WHERE tc.constraint_type = 'PRIMARY KEY' and tc.table_name='" + result[0] + "';")
        pknameList = cur.fetchall()
        pknames = []
        for pkname in pknameList:
            pknameJson = {}
            pknameJson['column_name'] = snakeToCamel(pkname[0])
            pknameJson['upper_column_name'] = snakeToUpperCamel(pkname[0])
            pknameJson['data_type'] = pkname[1]
            pknameJson['conv_type'] = typeConversion(pkname[1])
            pknames.append(pknameJson)
        res.append(
            {
                'tbl_name': result[0],
                'camel_tbl_name': snakeToCamel(result[0]),
                'upper_camel_tbl_name': snakeToUpperCamel(result[0]),
                'upper_snake_tbl_name': snakeToUpperSnake(result[0]),
                'path': '/' + camelToPath(snakeToCamel(result[0])),
                'columns': columns,
                'pknames': pknames
            })

    cur.close()
    connector.close()
    return res


def getRequestParams(columns):
    res = ""
    for column in columns:
        res += '    private String ' + column['column_name'] + ';\n'
    res += '\n'
    res += '    private String orderBy = "1";\n'
    res += '    private String ascOrDesc = "1";\n'
    res += '    private String limit = "100";\n'
    res += '    private String offset = "0";\n'
    return res


def createOrEditOrDeleteRequestParams(columns):
    res = ""
    for column in columns:
        res += '    private String ' + column['column_name'] + ';\n'
    return res


def responseParams(columns, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for column in columns:
        res += indentStr + 'private ' + column['conv_type'] + ' ' + column['column_name'] + ';\n'
    return res


def getListCountParams(columns, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for column in columns:
        res += indentStr + column['conv_type'] + ' ' + column['column_name'] + ',\n'
    return res[0:-2]


def selectListCountParams(columns, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for column in columns:
        res += indentStr + column['column_name'] + ',\n'
    return res[0:-2]


def editpkvals(tbl_name, pknames):
    res = ""
    for pkname in pknames:
        res += tbl_name + '.get' + pkname['upper_column_name'] + '(),'
    return res[0:-1]


def getordelpkparams(pknames):
    res = ""
    for pkname in pknames:
        res += pkname['conv_type'] + ' ' + pkname['column_name'] + ', '
    return res[0:-2]


def getordelpkvals(pknames):
    res = ""
    for pkname in pknames:
        res += pkname['column_name'] + ', '
    return res[0:-2]


def getListCountRequestVals(columns, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for column in columns:
        res += indentStr + parsetype(column['conv_type'], 'request.get' + column['upper_column_name'] + '()') + ',\n'
    return res[0:-2]


def setTmpList(columns, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for column in columns:
        res += indentStr + '.set' + column['upper_column_name'] + '(dto.get' + column['upper_column_name'] + '())\n'
    return res[0:-1]


def pkparamsSet(pknames, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for pkname in pknames:
        res += indentStr + '.set' + pkname['upper_column_name'] + '(id)\n'
    return res[0:-1]


def setdto(columns, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for column in columns:
        res += indentStr + 'dto.set' + column['upper_column_name'] + '(' + \
               parsetype(column['conv_type'], 'request.get' + column['upper_column_name'] + '()') + ');\n'
    return res[0:-1]


def setResponsedto(pknames, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for pkname in pknames:
        res += indentStr + '.set' + pkname['upper_column_name'] + '(' + \
               parsetype(pkname['conv_type'], 'dto.get' + pkname['upper_column_name'] + '()') + ')\n'
    return res[0:-1]


def getordelpkparamsController(pknames, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for pkname in pknames:
        res += indentStr + 'request.get' + pkname['upper_column_name'] + '(),\n'
    return res[0:-2]


def setMaxIdPknames(pknames):
    res = ""
    for pkname in pknames:
        res = '.set' + pkname['upper_column_name'] + '(maxId);'
    return res


def pathparams(pknames):
    res = ""
    for pkname in pknames:
        res += '/{' + pkname['column_name'] + '}'
    return res


def daoParams(columns, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for column in columns:
        res += indentStr + '@Param("' + column['column_name'] + '") ' + \
               column['conv_type'] + ' ' + column['column_name'] + ',\n'
    return res[0:-2]


def idFormatterConstant(db, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for tbl in db:
        res += indentStr + 'public static final String ' + \
               tbl['upper_snake_tbl_name'] + '_ID_PREFIX = "' + tbl['camel_tbl_name'] + '";\n'
        maximumLength = 8
        for column in tbl['columns']:
            if not column['character_maximum_length'] is None:
                maximumLength = column['character_maximum_length']
                break
        res += indentStr + 'public static final String ' + \
               tbl['upper_snake_tbl_name'] + '_ID_FORMAT = ' + tbl['upper_snake_tbl_name'] + \
               '_ID_PREFIX + "%' + str(maximumLength).zfill(2) + 'd";\n'

    return res[0:-1]


def mybatisTblTmp(db):
    res = ""
    for tbl in db:
        res += '    <table tableName="' + \
               tbl['tbl_name'] + '"\n' \
                                 '      enableInsert="true" enableSelectByPrimaryKey="true"\n' \
                                 '      enableSelectByExample="false" enableUpdateByPrimaryKey="true"\n' \
                                 '      enableUpdateByExample="false" enableDeleteByPrimaryKey="true"\n' \
                                 '      enableDeleteByExample="false" enableCountByExample="false"\n' \
                                 '      selectByExampleQueryId="false" modelType="flat">\n' \
                                 '    </table>\n'

    return res[0:-1]


def maxcolumns(pknames):
    res = ""
    for pkname in pknames:
        res += '      MAX(' + camelToSnake(pkname['column_name']) + ') as ' + camelToSnake(
            pkname['column_name']) + ',\n'
    return res[0:-2]


def resultMap(columns, pknames, indent=1):
    res = ""
    indentStr = ""
    for i in range(indent):
        indentStr += '    '
    for pkname in pknames:
        dataType = dataTypeConversion(pkname['data_type'])
        res += indentStr + '<id column="' + camelToSnake(pkname['column_name']) + '" jdbcType="' + \
               dataType + '" property="' + pkname['column_name'] + '" />\n'
    for column in columns:
        resultFlg = True
        for pkname in pknames:
            if pkname['column_name'] == column['column_name']:
                resultFlg = False
                break
        if resultFlg:
            dataType = dataTypeConversion(column['data_type'])
            res += indentStr + '<result column="' + camelToSnake(column['column_name']) + '" jdbcType="' + \
                   dataType + '" property="' + column['column_name'] + '" />\n'
    return res[0:-1]


def selectList(pknames):
    res = ""
    for pkname in pknames:
        res += '    <if test = "' + pkname['column_name'] + \
               ' != null">\n      AND ' + camelToSnake(pkname['column_name']) + \
               ' = #{' + pkname['column_name'] + '}\n    </if>\n'
    return res[0:-1]


def orderBy(columns):
    res = ""
    cnt = 1
    for column in columns:
        res += '    <if test="orderBy == ' + str(cnt) + '">\n      ' + \
               camelToSnake(column['column_name']) + '\n    </if>\n'
        cnt += 1;
    return res[0:-1]


def get_generator(db, settings):
    get_request(db, settings)
    get_controller(db, settings)
    get_service(db, settings)
    get_response(db, settings)
    get_dao(db, settings)


def get_request(db, settings):
    logging.debug('=====get_request start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/request/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'requestTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${classname}', 'Get' + tbl['upper_camel_tbl_name'] + 'Request')
        tmp = tmp.replace('${params}', getRequestParams(tbl['columns']))
        makeFile(dirpath, 'Get' + tbl['upper_camel_tbl_name'] + 'Request.java', tmp)


def get_controller(db, settings):
    logging.debug('=====get_controller start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/controller/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'get_controllerTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${getListCountRequestVals}', getListCountRequestVals(tbl['columns'], 4))
        tmp = tmp.replace('${setTmpList}', setTmpList(tbl['columns'], 6))
        tmp = tmp.replace('${path}', tbl['path'])
        makeFile(dirpath, 'Get' + tbl['upper_camel_tbl_name'] + 'Controller.java', tmp)
        tmp = openFile('./tmp', 'get_pk_controllerTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${setResponsedto}', setResponsedto(tbl['pknames'], 4))
        tmp = tmp.replace('${path}', tbl['path'] + pathparams(tbl['pknames']))
        tmp = tmp.replace('${getordelpkparamsController}', getordelpkparamsController(tbl['pknames'], 4))
        makeFile(dirpath, 'Get' + tbl['upper_camel_tbl_name'] + 'ByPrimaryKeyController.java', tmp)


def get_service(db, settings):
    logging.debug('=====get_service start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/service/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'serviceTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${getListCountParams}', getListCountParams(tbl['columns'], 3))
        tmp = tmp.replace('${getordelpkparams}', getordelpkparams(tbl['pknames']))
        makeFile(dirpath, tbl['upper_camel_tbl_name'] + 'Service.java', tmp)
        tmp = openFile('./tmp', 'serviceTmpImpl.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${getListCountParams}', getListCountParams(tbl['columns'], 3))
        tmp = tmp.replace('${selectListCountParams}', selectListCountParams(tbl['columns'], 3))
        tmp = tmp.replace('${upper_snake_tbl_name}', tbl['upper_snake_tbl_name'])
        tmp = tmp.replace('${editpkvals}', editpkvals(tbl['camel_tbl_name'], tbl['pknames']))
        tmp = tmp.replace('${getordelpkparams}', getordelpkparams(tbl['pknames']))
        tmp = tmp.replace('${getordelpkvals}', getordelpkvals(tbl['pknames']))
        tmp = tmp.replace('${setMaxIdPknames}', setMaxIdPknames(tbl['pknames']))
        tmp = tmp.replace('${uppername}', settings['name'][0].upper() + settings['name'][1:])
        makeFile(dirpath, tbl['upper_camel_tbl_name'] + 'ServiceImpl.java', tmp)


def get_response(db, settings):
    logging.debug('=====get_response start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/response/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'get_responseTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${classname}', 'Get' + tbl['upper_camel_tbl_name'] + 'Response')
        tmp = tmp.replace('${params}', responseParams(tbl['columns'], 2))
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        makeFile(dirpath, 'Get' + tbl['upper_camel_tbl_name'] + 'Response.java', tmp)
        tmp = openFile('./tmp', 'responseTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${classname}', 'Get' + tbl['upper_camel_tbl_name'] + 'ByPrimaryKeyResponse')
        tmp = tmp.replace('${params}', responseParams(tbl['columns']))
        makeFile(dirpath, 'Get' + tbl['upper_camel_tbl_name'] + 'ByPrimaryKeyResponse.java', tmp)


def get_dao(db, settings):
    logging.debug('=====get_dao start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + settings['project_path'].replace('.', '/') + '/dao/'
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'daoTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${daoParams}', daoParams(tbl['columns'], 3))
        makeFile(dirpath, tbl['upper_camel_tbl_name'] + 'MapperImpl.java', tmp)
        logging.debug('create ' + tbl['camel_tbl_name'] + ' xml')
        dirpath = './generator/' + settings['name'] + '/src/main/resources/' + \
                  settings['project_path'].replace('.', '/') + '/dao/'
        makeDir(dirpath)
        tmp = openFile('./tmp', 'mapperImplTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${maxcolumns}', maxcolumns(tbl['pknames']))
        tmp = tmp.replace('${resultMap}', resultMap(tbl['columns'], tbl['pknames']))
        tmp = tmp.replace('${selectList}', selectList(tbl['pknames']))
        tmp = tmp.replace('${orderBy}', orderBy(tbl['columns']))
        makeFile(dirpath, tbl['upper_camel_tbl_name'] + 'MapperImpl.xml', tmp)


def create_generator(db, settings):
    create_request(db, settings)
    create_controller(db, settings)
    create_service(db, settings)
    create_response(db, settings)


def create_request(db, settings):
    logging.debug('=====create_request start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/request/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'requestTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${classname}', 'Create' + tbl['upper_camel_tbl_name'] + 'Request')
        tmp = tmp.replace('${params}', createOrEditOrDeleteRequestParams(tbl['columns']))
        makeFile(dirpath, 'Create' + tbl['upper_camel_tbl_name'] + 'Request.java', tmp)


def create_controller(db, settings):
    logging.debug('=====create_controller start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/controller/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        if len(tbl['pknames']) > 1:
            tmp = openFile('./tmp', 'create_controllerTmp2.txt')
        else:
            tmp = openFile('./tmp', 'create_controllerTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${path}', tbl['path'])
        tmp = tmp.replace('${pkparamsSet}', pkparamsSet(tbl['pknames'], 6))
        tmp = tmp.replace('${setdto}', setdto(tbl['columns'], 4))
        makeFile(dirpath, 'Create' + tbl['upper_camel_tbl_name'] + 'Controller.java', tmp)


def create_service(db, settings):
    logging.debug('=====create_service start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/service/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'serviceTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${getListCountParams}', getListCountParams(tbl['columns'], 3))
        tmp = tmp.replace('${selectListCountParams}', selectListCountParams(tbl['columns'], 3))
        tmp = tmp.replace('${upper_snake_tbl_name}', tbl['upper_snake_tbl_name'])
        tmp = tmp.replace('${editpkvals}', editpkvals(tbl['camel_tbl_name'], tbl['pknames']))
        tmp = tmp.replace('${getordelpkparams}', getordelpkparams(tbl['pknames']))
        tmp = tmp.replace('${getordelpkvals}', getordelpkvals(tbl['pknames']))
        tmp = tmp.replace('${uppername}', settings['name'][0].upper() + settings['name'][1:])
        makeFile(dirpath, tbl['upper_camel_tbl_name'] + 'Service.java', tmp)


def create_response(db, settings):
    logging.debug('=====create_response start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/response/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'responseTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${classname}', 'Create' + tbl['upper_camel_tbl_name'] + 'Response')
        tmp = tmp.replace('${params}', responseParams(tbl['columns']))
        makeFile(dirpath, 'Create' + tbl['upper_camel_tbl_name'] + 'Response.java', tmp)


def edit_generator(db, settings):
    edit_request(db, settings)
    edit_controller(db, settings)
    edit_service(db, settings)


def edit_request(db, settings):
    logging.debug('=====edit_request start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/request/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'requestTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${classname}', 'Edit' + tbl['upper_camel_tbl_name'] + 'Request')
        tmp = tmp.replace('${params}', createOrEditOrDeleteRequestParams(tbl['columns']))
        makeFile(dirpath, 'Edit' + tbl['upper_camel_tbl_name'] + 'Request.java', tmp)


def edit_controller(db, settings):
    logging.debug('=====edit_controller start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/controller/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'edit_controllerTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${path}', tbl['path'])
        tmp = tmp.replace('${setdto}', setdto(tbl['columns'], 4))
        makeFile(dirpath, 'Edit' + tbl['upper_camel_tbl_name'] + 'Controller.java', tmp)


def edit_service(db, settings):
    logging.debug('=====edit_service start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/service/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'serviceTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${getListCountParams}', getListCountParams(tbl['columns'], 3))
        tmp = tmp.replace('${selectListCountParams}', selectListCountParams(tbl['columns'], 3))
        tmp = tmp.replace('${upper_snake_tbl_name}', tbl['upper_snake_tbl_name'])
        tmp = tmp.replace('${editpkvals}', editpkvals(tbl['camel_tbl_name'], tbl['pknames']))
        tmp = tmp.replace('${getordelpkparams}', getordelpkparams(tbl['pknames']))
        tmp = tmp.replace('${getordelpkvals}', getordelpkvals(tbl['pknames']))
        tmp = tmp.replace('${uppername}', settings['name'][0].upper() + settings['name'][1:])
        makeFile(dirpath, tbl['upper_camel_tbl_name'] + 'Service.java', tmp)


def delete_generator(db, settings):
    delete_request(db, settings)
    delete_controller(db, settings)
    delete_service(db, settings)


def delete_request(db, settings):
    logging.debug('=====delete_request start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/request/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('delete ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'requestTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${classname}', tbl['upper_camel_tbl_name'] + 'PathParameter')
        tmp = tmp.replace('${params}', createOrEditOrDeleteRequestParams(tbl['pknames']))
        makeFile(dirpath, tbl['upper_camel_tbl_name'] + 'PathParameter.java', tmp)


def delete_controller(db, settings):
    logging.debug('=====delete_controller start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/controller/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'delete_controllerTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${path}', tbl['path'] + pathparams(tbl['pknames']))
        tmp = tmp.replace('${getordelpkparamsController}', getordelpkparamsController(tbl['pknames'], 4))
        makeFile(dirpath, 'Delete' + tbl['upper_camel_tbl_name'] + 'Controller.java', tmp)


def delete_service(db, settings):
    logging.debug('=====delete_service start=====')
    logging.debug('make dir')
    for tbl in db:
        dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
                  settings['project_path'].replace('.', '/') + '/service/' + tbl['camel_tbl_name']
        makeDir(dirpath)
        logging.debug('create ' + tbl['camel_tbl_name'])
        tmp = openFile('./tmp', 'serviceTmp.txt')
        tmp = tmp.replace('${project_path}', settings['project_path'])
        tmp = tmp.replace('${tblname}', tbl['camel_tbl_name'])
        tmp = tmp.replace('${uppertblname}', tbl['upper_camel_tbl_name'])
        tmp = tmp.replace('${getListCountParams}', getListCountParams(tbl['columns'], 3))
        tmp = tmp.replace('${selectListCountParams}', selectListCountParams(tbl['columns'], 3))
        tmp = tmp.replace('${upper_snake_tbl_name}', tbl['upper_snake_tbl_name'])
        tmp = tmp.replace('${editpkvals}', editpkvals(tbl['camel_tbl_name'], tbl['pknames']))
        tmp = tmp.replace('${getordelpkparams}', getordelpkparams(tbl['pknames']))
        tmp = tmp.replace('${getordelpkvals}', getordelpkvals(tbl['pknames']))
        tmp = tmp.replace('${uppername}', settings['name'][0].upper() + settings['name'][1:])
        makeFile(dirpath, tbl['upper_camel_tbl_name'] + 'Service.java', tmp)


def application_generator(settings):
    logging.debug('=====application_generator start=====')
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/'
    makeDir(dirpath)
    logging.debug('create application')
    tmp = openFile('./tmp', 'applicationTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${uppername}', settings['name'][0].upper() + settings['name'][1:])
    makeFile(dirpath, settings['name'][0].upper() + settings['name'][1:] + 'Application.java', tmp)


def id_formatter_generator(db, settings):
    logging.debug('=====id_formatter_generator start=====')
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/constant/'
    makeDir(dirpath)
    logging.debug('create IdFormatterConstant')
    tmp = openFile('./tmp', 'IdFormatterTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${idFormatterConstant}', idFormatterConstant(db))
    makeFile(dirpath, 'IdFormatterConstant.java', tmp)


def exception_generator(settings):
    logging.debug('=====exception_generator start=====')
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/exception/'
    makeDir(dirpath)
    logging.debug('create ' + settings['name'][0].upper() + settings['name'][1:] + 'Exception')
    tmp = openFile('./tmp', 'exceptionTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${uppername}', settings['name'][0].upper() + settings['name'][1:])
    makeFile(dirpath, settings['name'][0].upper() + settings['name'][1:] + 'Exception.java', tmp)
    logging.debug('create RequestParameterException')
    tmp = openFile('./tmp', 'requestParameterExceptionTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${uppername}', settings['name'][0].upper() + settings['name'][1:])
    makeFile(dirpath, 'RequestParameterException.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/exception/entity/'
    makeDir(dirpath)
    logging.debug('create ErrorParam')
    tmp = openFile('./tmp', 'errorParamTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'ErrorParam.java', tmp)


def template_generator(settings):
    logging.debug('=====template_generator start=====')
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/controller/'
    makeDir(dirpath)
    logging.debug('create BaseController')
    tmp = openFile('./tmp', 'baseControllerTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${uppername}', settings['name'][0].upper() + settings['name'][1:])
    makeFile(dirpath, 'BaseController.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/constant/'
    makeDir(dirpath)
    logging.debug('create Constant')
    tmp = openFile('./tmp', 'constantTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'Constant.java', tmp)
    logging.debug('create ApiErrorMessage')
    tmp = openFile('./tmp', 'apiErrorMessageTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'ApiErrorMessage.java', tmp)
    logging.debug('create ResultCode')
    tmp = openFile('./tmp', 'resultCodeTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'ResultCode.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/common/'
    makeDir(dirpath)
    logging.debug('create Functions')
    tmp = openFile('./tmp', 'functionsTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'Functions.java', tmp)
    logging.debug('create CommonUtils')
    tmp = openFile('./tmp', 'commonUtilsTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'CommonUtils.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/validations/'
    makeDir(dirpath)
    logging.debug('create booleanType')
    tmp = openFile('./tmp', 'booleanTypeTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'BooleanType.java', tmp)
    logging.debug('create DateType')
    tmp = openFile('./tmp', 'dateTypeTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'DateType.java', tmp)
    logging.debug('create HalfAlphanumeric')
    tmp = openFile('./tmp', 'halfAlphanumericTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'HalfAlphanumeric.java', tmp)
    logging.debug('create IntegerType')
    tmp = openFile('./tmp', 'integerTypeTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'IntegerType.java', tmp)
    logging.debug('create LongType')
    tmp = openFile('./tmp', 'longTypeTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'LongType.java', tmp)
    logging.debug('create NoDuplicate')
    tmp = openFile('./tmp', 'noDuplicateTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'NoDuplicate.java', tmp)
    logging.debug('create NumberType')
    tmp = openFile('./tmp', 'numberTypeTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'NumberType.java', tmp)
    logging.debug('create ShortType')
    tmp = openFile('./tmp', 'shortTypeTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'ShortType.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/response/'
    makeDir(dirpath)
    logging.debug('create ApiResponse')
    tmp = openFile('./tmp', 'apiResponseTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'ApiResponse.java', tmp)
    logging.debug('create ApiResponseOptional')
    tmp = openFile('./tmp', 'apiResponseOptionalTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'ApiResponseOptional.java', tmp)
    logging.debug('create RequestParameterErrorResponse')
    tmp = openFile('./tmp', 'requestParameterErrorResponseTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'RequestParameterErrorResponse.java', tmp)


def pom_generator(settings):
    logging.debug('=====pom_generator start=====')
    logging.debug('make dir')
    dirpath = './generator/' + settings['name']
    makeDir(dirpath)
    logging.debug('create Constant')
    tmp = openFile('./tmp', 'pomTmp.txt')
    tmp = tmp.replace('@{name}', settings['name'])
    tmp = tmp.replace('@{description}', settings['description'])
    makeFile(dirpath, 'pom.xml', tmp)


def mybatis_generator(db, settings):
    logging.debug('=====mybatis_generator start=====')
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/resources/'
    makeDir(dirpath)
    logging.debug('create generatorConfig')
    tmp = openFile('./tmp', 'generatorConfigTmp.txt')
    tmp = tmp.replace('@{name}', settings['name'])
    tmp = tmp.replace('@{dbname}', settings['db']['dbname'])
    tmp = tmp.replace('@{user}', settings['db']['user'])
    tmp = tmp.replace('@{password}', settings['db']['password'])
    tmp = tmp.replace('@{host}', settings['db']['host'])
    tmp = tmp.replace('@{port}', settings['db']['port'])
    tmp = tmp.replace('@{tbl}', mybatisTblTmp(db))
    makeFile(dirpath, 'generatorConfigTmp.xml', tmp)


def banner_generator(settings):
    logging.debug('=====banner_generator start=====')
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/resources/'
    makeDir(dirpath)
    logging.debug('create banner')
    tmp = openFile('./tmp', 'bannerTmp.txt')
    makeFile(dirpath, 'banner.txt', tmp)


def properties_generator(settings):
    logging.debug('=====properties_generator start=====')
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/resources/'
    makeDir(dirpath)
    logging.debug('create properties')
    tmp = openFile('./tmp', 'propertiesTmp.txt')
    tmp = tmp.replace('@{name}', settings['name'])
    tmp = tmp.replace('@{dbname}', settings['db']['dbname'])
    tmp = tmp.replace('@{user}', settings['db']['user'])
    tmp = tmp.replace('@{password}', settings['db']['password'])
    tmp = tmp.replace('@{host}', settings['db']['host'])
    tmp = tmp.replace('@{port}', settings['db']['port'])
    makeFile(dirpath, 'application.properties', tmp)


def authorization_generator(settings):
    logging.debug('=====authorization_generator start=====')
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/config/'
    makeDir(dirpath)
    logging.debug('create SecurityConfig')
    tmp = openFile('./tmp', 'securityConfigTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'SecurityConfig.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/service/'
    makeDir(dirpath)
    logging.debug('create UserDetailsServiceImpl')
    tmp = openFile('./tmp', 'userDetailsServiceImpl.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${auth_tblname}', snakeToUpperCamel(settings['authorization']['authTbl']['tblname']))
    tmp = tmp.replace('${upper_username_column}',
                      snakeToUpperCamel(settings['authorization']['authTbl']['usernameColumn']))
    tmp = tmp.replace('${upper_passward_column}',
                      snakeToUpperCamel(settings['authorization']['authTbl']['passwardColumn']))
    tmp = tmp.replace('${upper_authority_column}',
                      snakeToUpperCamel(settings['authorization']['authTbl']['authorityColumn']))
    makeFile(dirpath, 'UserDetailsServiceImpl.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/service/login/'
    makeDir(dirpath)
    logging.debug('create LoginService')
    tmp = openFile('./tmp', 'loginServiceTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${auth_tblname}', snakeToUpperCamel(settings['authorization']['authTbl']['tblname']))
    makeFile(dirpath, 'LoginService.java', tmp)
    logging.debug('create LoginServiceImpl')
    tmp = openFile('./tmp', 'loginServiceImplTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${auth_tblname}', snakeToUpperCamel(settings['authorization']['authTbl']['tblname']))
    tmp = tmp.replace('${upper_lock_column}', snakeToUpperCamel(settings['authorization']['authTbl']['lockColumn']))
    tmp = tmp.replace('${upper_passward_column}',
                      snakeToUpperCamel(settings['authorization']['authTbl']['passwardColumn']))
    tmp = tmp.replace('${uppername}', settings['name'][0].upper() + settings['name'][1:])
    makeFile(dirpath, 'LoginServiceImpl.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/controller/login/'
    makeDir(dirpath)
    logging.debug('create LoginController')
    tmp = openFile('./tmp', 'loginControllerTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${auth_tblname}', snakeToUpperCamel(settings['authorization']['authTbl']['tblname']))
    tmp = tmp.replace('${upper_username_column}',
                      snakeToUpperCamel(settings['authorization']['authTbl']['usernameColumn']))
    tmp = tmp.replace('${upper_authority_column}',
                      snakeToUpperCamel(settings['authorization']['authTbl']['authorityColumn']))
    makeFile(dirpath, 'LoginController.java', tmp)
    logging.debug('create LogoutController')
    tmp = openFile('./tmp', 'logoutControllerTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'LogoutController.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/controller/user/'
    makeDir(dirpath)
    logging.debug('create EditUserLockController')
    tmp = openFile('./tmp', 'editUserLockControllerTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${auth_tblname}', snakeToCamel(settings['authorization']['authTbl']['tblname']))
    tmp = tmp.replace('${upper_auth_tblname}', snakeToUpperCamel(settings['authorization']['authTbl']['tblname']))
    tmp = tmp.replace('${upper_username_column}',
                      snakeToUpperCamel(settings['authorization']['authTbl']['usernameColumn']))
    tmp = tmp.replace('${upper_lock_column}', snakeToUpperCamel(settings['authorization']['authTbl']['lockColumn']))
    makeFile(dirpath, 'EditUserLockController.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/request/login/'
    makeDir(dirpath)
    logging.debug('create LoginRequest')
    tmp = openFile('./tmp', 'loginRequestTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'LoginRequest.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/request/user/'
    makeDir(dirpath)
    logging.debug('create EditUserLockRequest')
    tmp = openFile('./tmp', 'editUserLockRequestTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    makeFile(dirpath, 'EditUserLockRequest.java', tmp)
    logging.debug('make dir')
    dirpath = './generator/' + settings['name'] + '/src/main/java/' + \
              settings['project_path'].replace('.', '/') + '/response/login/'
    makeDir(dirpath)
    logging.debug('create LoginResponse')
    tmp = openFile('./tmp', 'loginResponseTmp.txt')
    tmp = tmp.replace('${project_path}', settings['project_path'])
    tmp = tmp.replace('${username_column}',
                      snakeToCamel(settings['authorization']['authTbl']['usernameColumn']))
    tmp = tmp.replace('${authority_column}',
                      snakeToCamel(settings['authorization']['authTbl']['authorityColumn']))
    makeFile(dirpath, 'LoginResponse.java', tmp)


if __name__ == '__main__':
    # ログ初期処理
    makeDir('./log')
    logging.basicConfig(level=logging.DEBUG, filename="./log/app.log",
                        format="%(asctime)s  %(levelname)s  %(message)s")

    # 初期処理
    settings = json.load(open('setting.json', 'r'))  # 設定取得
    db = get_db(settings)  # DB情報取得

    # コード生成処理
    if settings['generator']['get']:
        get_generator(db, settings)
    if settings['generator']['create']:
        create_generator(db, settings)
    if settings['generator']['edit']:
        edit_generator(db, settings)
    if settings['generator']['delete']:
        delete_generator(db, settings)
    if settings['option']['Main']:
        application_generator(settings)
    if settings['option']['IdFormatterConstant']:
        id_formatter_generator(db, settings)
    if settings['option']['Exception']:
        exception_generator(settings)
    if settings['option']['Template']:
        template_generator(settings)
    if settings['project']['pom']:
        pom_generator(settings)
    if settings['project']['mybatis']:
        mybatis_generator(db, settings)
    if settings['project']['banner']:
        banner_generator(settings)
    if settings['project']['properties']:
        properties_generator(settings)
    if settings['authorization']['authFlg']:
        authorization_generator(settings)
    with open('./generator.json', 'w') as f:
        json.dump(db, f, indent=2)
