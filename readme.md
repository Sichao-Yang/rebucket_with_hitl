# implementation on rebucket

## intro

该项目为针对微软2012年文章 [rebucket](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/rebucket-icse2012.pdf) 的实现，同时引入了human in the loop的改进，可以应用在序列类数据的 无|半监督聚类上。

## structure

项目里分了三个文件夹：

```
├───baseline    v1版本的示例notebook，对应的 *.json 数据文件
├───hitl        v2版本的示例notebook，对应的 *.json 数据文件，以及*.yml config文件
└───src         rebucket算法（距离指标和分层聚类），grid search超参优化，hitl交互方法实现
```

## quick start

项目里有两个例子：

1. 在baseline里有一个`impl.ipynb`的例子，只包含了refrecne里说到的`rebucket`算法的使用
2. 在hitl里有一个`impl.ipynb`的例子，除了`rebucket`，还包含了`HumanInTheLoop`的使用

## requirements

因为所有的implementation都是基于python原生的，所以除了 `numpy, json, yaml` 三个热门库几乎没有依赖


## reference

Dang, Yingnong, Rongxin Wu, Hongyu Zhang, Dongmei Zhang, and Peter Nobel. “ReBucket: A Method for Clustering Duplicate Crash Reports Based on Call Stack Similarity.” In 2012 34th International Conference on Software Engineering (ICSE), 1084–93. Zurich: IEEE, 2012. https://doi.org/10.1109/ICSE.2012.6227111.
